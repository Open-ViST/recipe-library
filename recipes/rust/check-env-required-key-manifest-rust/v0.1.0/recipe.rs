use std::collections::{BTreeMap, BTreeSet};
use std::io::{self, Read, Write};

struct AssignmentInfo {
    positions: Vec<usize>,
    has_empty: bool,
}

fn valid_key(key: &str) -> bool {
    let bytes = key.as_bytes();
    if bytes.is_empty() || bytes.len() > 64 {
        return false;
    }
    let first = bytes[0];
    if !(first.is_ascii_alphabetic() || first == b'_') {
        return false;
    }
    bytes[1..]
        .iter()
        .all(|&b| b.is_ascii_alphanumeric() || b == b'_')
}

fn json_string(out: &mut String, text: &str) {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    out.push('"');
    for ch in text.chars() {
        match ch {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\u{0000}'..='\u{001f}' => {
                let n = ch as usize;
                out.push_str("\\u00");
                out.push(HEX[n >> 4] as char);
                out.push(HEX[n & 15] as char);
            }
            _ => out.push(ch),
        }
    }
    out.push('"');
}

fn json_names(out: &mut String, names: &[&str]) {
    out.push('[');
    for (index, name) in names.iter().enumerate() {
        if index != 0 {
            out.push(',');
        }
        json_string(out, name);
    }
    out.push(']');
}

fn audit() -> Result<String, ()> {
    let mut bytes = Vec::new();
    {
        let stdin = io::stdin();
        let mut bounded = stdin.lock().take(65537);
        bounded.read_to_end(&mut bytes).map_err(|_| ())?;
    }
    if bytes.len() > 65536 {
        return Err(());
    }
    let text = std::str::from_utf8(&bytes).map_err(|_| ())?;
    if text.starts_with('\u{feff}') {
        return Err(());
    }
    if bytes.iter().any(|&b| (b < 32 && b != b'\n') || b == 127) {
        return Err(());
    }

    let mut selectors: BTreeSet<String> = BTreeSet::new();
    let mut assignments: BTreeMap<String, AssignmentInfo> = BTreeMap::new();
    let mut in_assignments = false;
    let mut record_count = 0usize;
    let mut value_bytes = 0usize;

    for line in text.split('\n') {
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        if line == "---" {
            if in_assignments {
                return Err(());
            }
            in_assignments = true;
            continue;
        }
        if !in_assignments {
            if !valid_key(line) || selectors.len() >= 100 {
                return Err(());
            }
            if !selectors.insert(line.to_owned()) {
                return Err(());
            }
        } else {
            record_count += 1;
            if record_count > 100 {
                return Err(());
            }
            let (key, value) = line.split_once('=').ok_or(())?;
            if !valid_key(key) {
                return Err(());
            }
            value_bytes += value.len();
            if value_bytes > 1024 {
                return Err(());
            }
            let info = assignments.entry(key.to_owned()).or_insert_with(|| {
                AssignmentInfo {
                    positions: Vec::new(),
                    has_empty: false,
                }
            });
            info.positions.push(record_count);
            info.has_empty |= value.is_empty();
        }
    }
    if !in_assignments {
        return Err(());
    }

    let mut missing: Vec<&str> = Vec::new();
    let mut empty: Vec<&str> = Vec::new();
    let mut unknown: Vec<&str> = Vec::new();
    for key in &selectors {
        match assignments.get(key) {
            None => missing.push(key.as_str()),
            Some(info) if info.has_empty => empty.push(key.as_str()),
            Some(_) => {}
        }
    }
    for key in assignments.keys() {
        if !selectors.contains(key) {
            unknown.push(key.as_str());
        }
    }

    let mut out = String::new();
    out.push_str("{\"missing\":");
    json_names(&mut out, &missing);
    out.push_str(",\"empty\":");
    json_names(&mut out, &empty);
    out.push_str(",\"duplicates\":[");
    let mut first_duplicate = true;
    for (key, info) in &assignments {
        if info.positions.len() < 2 {
            continue;
        }
        if !first_duplicate {
            out.push(',');
        }
        first_duplicate = false;
        out.push_str("{\"key\":");
        json_string(&mut out, key);
        out.push_str(",\"positions\":[");
        for (index, position) in info.positions.iter().enumerate() {
            if index != 0 {
                out.push(',');
            }
            out.push_str(&position.to_string());
        }
        out.push_str("]}");
    }
    out.push_str("],\"unknown\":");
    json_names(&mut out, &unknown);
    out.push_str("}\n");
    Ok(out)
}

fn invalid_input() -> ! {
    let stderr = io::stderr();
    let _ = stderr.lock().write_all(b"error: invalid input\n");
    std::process::exit(2)
}

fn main() {
    if std::env::args_os().skip(1).next().is_some() {
        invalid_input();
    }
    let output = match audit() {
        Ok(output) => output,
        Err(()) => invalid_input(),
    };
    let stdout = io::stdout();
    let mut writer = stdout.lock();
    if writer.write_all(output.as_bytes()).is_err() {
        std::process::exit(2);
    }
    if writer.flush().is_err() {
        std::process::exit(2);
    }
}
