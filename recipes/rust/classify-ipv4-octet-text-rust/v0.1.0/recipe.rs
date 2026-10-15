use std::io::{self, Read, Write};

fn canonical_ipv4(text: &str) -> bool {
    let mut parts = text.split('.');
    for _ in 0..4 {
        let part = match parts.next() {
            Some(part) => part,
            None => return false,
        };
        let bytes = part.as_bytes();
        if bytes.is_empty() || bytes.len() > 3 {
            return false;
        }
        if bytes.len() > 1 && bytes[0] == b'0' {
            return false;
        }
        let mut value: u16 = 0;
        for &byte in bytes {
            if !byte.is_ascii_digit() {
                return false;
            }
            value = value * 10 + u16::from(byte - b'0');
        }
        if value > 255 {
            return false;
        }
    }
    parts.next().is_none()
}

fn prepare_output() -> Result<String, ()> {
    if std::env::args_os().skip(1).next().is_some() {
        return Err(());
    }

    let stdin = io::stdin();
    let mut reader = stdin.lock().take(65_537);
    let mut input = Vec::new();
    reader.read_to_end(&mut input).map_err(|_| ())?;
    if input.len() > 65_536 {
        return Err(());
    }

    let text = std::str::from_utf8(&input).map_err(|_| ())?;
    if text.starts_with('\u{feff}') || input.contains(&b'\r') {
        return Err(());
    }

    let mut lines = Vec::new();
    for line in text.split('\n') {
        if line.is_empty() {
            continue;
        }
        if line.len() > 256 || lines.len() >= 100 {
            return Err(());
        }
        lines.push(line);
    }

    // Every input limit has been validated before classification starts.
    let mut output = String::from("{\"valid\":[");
    for (index, line) in lines.iter().enumerate() {
        if index != 0 {
            output.push(',');
        }
        output.push_str(if canonical_ipv4(line) { "true" } else { "false" });
    }
    output.push_str("]}\n");
    Ok(output)
}

fn main() {
    match prepare_output() {
        Ok(output) => {
            let stdout = io::stdout();
            let mut writer = stdout.lock();
            if writer.write_all(output.as_bytes()).is_err() {
                std::process::exit(2);
            }
            if writer.flush().is_err() {
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
