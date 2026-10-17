use std::collections::BTreeSet;
use std::io::{self, Read, Write};

fn valid_key(key: &str) -> bool {
    let bytes = key.as_bytes();
    if bytes.is_empty() || bytes.len() > 64 {
        return false;
    }
    if !(bytes[0].is_ascii_alphabetic() || bytes[0] == b'_') {
        return false;
    }
    bytes[1..]
        .iter()
        .all(|b| b.is_ascii_alphanumeric() || *b == b'_')
}

fn json_string(output: &mut String, text: &str) {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    output.push('"');
    for ch in text.chars() {
        match ch {
            '"' => output.push_str("\\\""),
            '\\' => output.push_str("\\\\"),
            '\u{0000}'..='\u{001f}' => {
                let n = ch as usize;
                output.push_str("\\u00");
                output.push(HEX[n >> 4] as char);
                output.push(HEX[n & 15] as char);
            }
            _ => output.push(ch),
        }
    }
    output.push('"');
}

fn validate_and_render(input: &str) -> Result<String, ()> {
    if input.starts_with('\u{feff}') {
        return Err(());
    }
    if input.bytes().any(|b| (b < 32 && b != b'\n') || b == 127) {
        return Err(());
    }

    let mut selectors: BTreeSet<&str> = BTreeSet::new();
    let mut assignments: Vec<(&str, &str)> = Vec::new();
    let mut separator_seen = false;
    let mut total_value_bytes = 0usize;

    for line in input.split('\n') {
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        if line == "---" {
            if separator_seen {
                return Err(());
            }
            separator_seen = true;
            continue;
        }
        if !separator_seen {
            if !valid_key(line) || selectors.len() >= 100 {
                return Err(());
            }
            if !selectors.insert(line) {
                return Err(());
            }
        } else {
            if assignments.len() >= 100 {
                return Err(());
            }
            let (key, value) = line.split_once('=').ok_or(())?;
            if !valid_key(key) {
                return Err(());
            }
            total_value_bytes += value.len();
            if total_value_bytes > 1024 {
                return Err(());
            }
            assignments.push((key, value));
        }
    }
    if !separator_seen {
        return Err(());
    }

    // No successful output is constructed until all input is validated.
    let mut output = String::from("{\"assignments\":[");
    for (index, (key, value)) in assignments.iter().enumerate() {
        if index != 0 {
            output.push(',');
        }
        output.push_str("{\"key\":");
        json_string(&mut output, key);
        output.push_str(",\"value\":");
        if selectors.contains(*key) {
            json_string(&mut output, "[REDACTED]");
        } else {
            json_string(&mut output, value);
        }
        output.push('}');
    }
    output.push_str("]}\n");
    Ok(output)
}

fn run() -> Result<String, ()> {
    if std::env::args_os().nth(1).is_some() {
        return Err(());
    }
    let stdin = io::stdin();
    let mut reader = stdin.lock().take(65537);
    let mut bytes = Vec::new();
    reader.read_to_end(&mut bytes).map_err(|_| ())?;
    if bytes.len() > 65536 {
        return Err(());
    }
    let input = std::str::from_utf8(&bytes).map_err(|_| ())?;
    validate_and_render(input)
}

fn main() {
    match run() {
        Ok(output) => {
            let stdout = io::stdout();
            let mut writer = stdout.lock();
            if writer.write_all(output.as_bytes()).is_err() || writer.flush().is_err() {
                std::process::exit(2);
            }
        }
        Err(()) => {
            let stderr = io::stderr();
            let mut writer = stderr.lock();
            let _ = writer.write_all(b"error: invalid input\n");
            let _ = writer.flush();
            std::process::exit(2);
        }
    }
}
