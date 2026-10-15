use std::io::{self, Read, Write};

fn invalid_input() -> ! {
    let stderr = io::stderr();
    let mut err = stderr.lock();
    let _ = err.write_all(b"error: invalid input\n");
    std::process::exit(2);
}

fn parse_ipv4(text: &str) -> Option<[u8; 4]> {
    let mut parts = text.split('.');
    let mut address = [0u8; 4];
    for octet in &mut address {
        let part = parts.next()?;
        let bytes = part.as_bytes();
        if bytes.is_empty() || bytes.len() > 3 {
            return None;
        }
        if bytes.len() > 1 && bytes[0] == b'0' {
            return None;
        }
        let mut value = 0u16;
        for &byte in bytes {
            if !byte.is_ascii_digit() {
                return None;
            }
            value = value * 10 + u16::from(byte - b'0');
        }
        if value > 255 {
            return None;
        }
        *octet = value as u8;
    }
    if parts.next().is_some() {
        return None;
    }
    Some(address)
}

fn run() -> Result<String, ()> {
    let stdin = io::stdin();
    let mut reader = stdin.lock().take(65_537);
    let mut input = Vec::with_capacity(65_537);
    reader.read_to_end(&mut input).map_err(|_| ())?;
    if input.len() > 65_536 {
        return Err(());
    }

    let text = std::str::from_utf8(&input).map_err(|_| ())?;
    if text.starts_with('\u{feff}') || input.contains(&b'\r') {
        return Err(());
    }

    // Enforce all line limits before parsing or comparing any pairs.
    let mut lines = Vec::with_capacity(100);
    for line in text.split('\n') {
        if line.is_empty() {
            continue;
        }
        if line.len() > 256 || lines.len() == 100 {
            return Err(());
        }
        lines.push(line);
    }

    let mut shared = Vec::with_capacity(lines.len());
    for line in lines {
        let mut pair = line.split('|');
        let left = pair.next().ok_or(())?;
        let right = pair.next().ok_or(())?;
        if pair.next().is_some() {
            return Err(());
        }
        let a = parse_ipv4(left).ok_or(())?;
        let b = parse_ipv4(right).ok_or(())?;
        let mut count = 0u8;
        for i in 0..4 {
            if a[i] != b[i] {
                break;
            }
            count += 1;
        }
        shared.push(count);
    }

    // Construct successful output only after the entire input is valid.
    let mut output = String::with_capacity(213);
    output.push_str("{\"shared\":[");
    for (index, count) in shared.into_iter().enumerate() {
        if index != 0 {
            output.push(',');
        }
        output.push(char::from(b'0' + count));
    }
    output.push_str("]}\n");
    Ok(output)
}

fn main() {
    if std::env::args_os().skip(1).next().is_some() {
        invalid_input();
    }
    let output = match run() {
        Ok(output) => output,
        Err(()) => invalid_input(),
    };
    let stdout = io::stdout();
    let mut out = stdout.lock();
    if out.write_all(output.as_bytes()).is_err() {
        std::process::exit(2);
    }
}
