use std::io::{Read, Write};

fn invalid() -> ! {
    let stderr = std::io::stderr();
    let mut err = stderr.lock();
    let _ = err.write_all(b"error: invalid input\n");
    let _ = err.flush();
    std::process::exit(2);
}

fn main() {
    if std::env::args_os().skip(1).next().is_some() {
        invalid();
    }

    let stdin = std::io::stdin();
    let mut reader = stdin.lock().take(65_537);
    let mut input = Vec::new();
    if reader.read_to_end(&mut input).is_err() {
        invalid();
    }
    if input.len() > 65_536 {
        invalid();
    }

    let text = match std::str::from_utf8(&input) {
        Ok(text) => text,
        Err(_) => invalid(),
    };
    if text.starts_with('\u{feff}') || input.contains(&b'\r') {
        invalid();
    }

    // Enforce every retained-line limit before classifying any value.
    let mut lines = Vec::new();
    for line in text.split('\n') {
        if line.is_empty() {
            continue;
        }
        if line.len() > 256 || lines.len() >= 100 {
            invalid();
        }
        lines.push(line);
    }

    let mut values: Vec<i64> = Vec::with_capacity(lines.len());
    for line in lines {
        let bytes = line.as_bytes();
        if bytes.len() > 1 && bytes[0] == b'0' {
            invalid();
        }

        let mut value: i64 = 0;
        for &byte in bytes {
            if !byte.is_ascii_digit() {
                invalid();
            }
            // The previous value is at most 1,000,000, so this cannot overflow.
            value = value * 10 + i64::from(byte - b'0');
            if value > 1_000_000 {
                invalid();
            }
        }
        values.push(value);
    }

    // No successful stdout is emitted until all input has been validated.
    let mut output = String::from("{\"deltas\":[");
    for (index, pair) in values.windows(2).enumerate() {
        if index != 0 {
            output.push(',');
        }
        let delta: i64 = pair[1] - pair[0];
        output.push_str(&delta.to_string());
    }
    output.push_str("]}\n");

    let stdout = std::io::stdout();
    let mut out = stdout.lock();
    if out.write_all(output.as_bytes()).is_err() || out.flush().is_err() {
        std::process::exit(2);
    }
}
