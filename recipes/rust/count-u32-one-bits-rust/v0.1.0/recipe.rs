use std::io::{self, Read, Write};

fn invalid_input() -> ! {
    let stderr = io::stderr();
    let mut err = stderr.lock();
    let _ = err.write_all(b"error: invalid input\n");
    let _ = err.flush();
    std::process::exit(2);
}

fn prepare_output() -> Result<String, ()> {
    let stdin = io::stdin();
    let mut input = Vec::new();
    stdin.lock().take(65537).read_to_end(&mut input).map_err(|_| ())?;
    if input.len() > 65536 {
        return Err(());
    }

    let text = std::str::from_utf8(&input).map_err(|_| ())?;
    if text.starts_with('\u{feff}') || text.as_bytes().contains(&b'\r') {
        return Err(());
    }

    // Enforce all retained-line limits before interpreting any numbers.
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

    let mut counts = Vec::with_capacity(lines.len());
    for line in lines {
        let bytes = line.as_bytes();
        if bytes.len() > 1 && bytes[0] == b'0' {
            return Err(());
        }
        let mut value = 0u32;
        for &byte in bytes {
            if !byte.is_ascii_digit() {
                return Err(());
            }
            value = value.checked_mul(10)
                .and_then(|v| v.checked_add(u32::from(byte - b'0')))
                .ok_or(())?;
        }
        counts.push(value.count_ones());
    }

    let mut output = String::from("{\"ones\":[");
    for (index, count) in counts.iter().enumerate() {
        if index != 0 {
            output.push(',');
        }
        output.push_str(&count.to_string());
    }
    output.push_str("]}\n");
    Ok(output)
}

fn main() {
    if std::env::args_os().skip(1).next().is_some() {
        invalid_input();
    }
    let output = match prepare_output() {
        Ok(output) => output,
        Err(()) => invalid_input(),
    };

    let stdout = io::stdout();
    let mut out = stdout.lock();
    if out.write_all(output.as_bytes()).is_err() || out.flush().is_err() {
        std::process::exit(1);
    }
}
