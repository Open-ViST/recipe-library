use std::io::{self, Read, Write};

fn build_output() -> Result<String, ()> {
    if std::env::args_os().skip(1).next().is_some() {
        return Err(());
    }

    // Read at most 65537 bytes, including the byte used to detect oversize input.
    let mut buffer = [0u8; 65537];
    let mut used = 0usize;
    {
        let stdin = io::stdin();
        let mut input = stdin.lock();
        loop {
            if used == buffer.len() {
                return Err(());
            }
            match input.read(&mut buffer[used..]) {
                Ok(0) => break,
                Ok(n) => used += n,
                Err(e) if e.kind() == io::ErrorKind::Interrupted => continue,
                Err(_) => return Err(()),
            }
        }
    }
    if used > 65536 {
        return Err(());
    }

    let text = std::str::from_utf8(&buffer[..used]).map_err(|_| ())?;
    if text.starts_with('\u{feff}') || text.as_bytes().contains(&b'\r') {
        return Err(());
    }

    // Enforce every line/count limit before parsing, sorting or deduplication.
    let mut lines: Vec<&str> = Vec::new();
    for line in text.split('\n') {
        if line.is_empty() {
            continue;
        }
        if line.len() > 256 || lines.len() >= 100 {
            return Err(());
        }
        lines.push(line);
    }

    let mut values: Vec<u32> = Vec::with_capacity(lines.len());
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
            // The previous value is at most 1000000, so this cannot overflow.
            value = value * 10 + u32::from(byte - b'0');
            if value > 1000000 {
                return Err(());
            }
        }
        values.push(value);
    }

    values.sort_unstable();
    values.dedup();

    let mut ranges: Vec<(u32, u32)> = Vec::new();
    for value in values {
        if let Some(last) = ranges.last_mut() {
            if value == last.1 + 1 {
                last.1 = value;
                continue;
            }
        }
        ranges.push((value, value));
    }

    let mut output = String::from("{\"ranges\":[");
    for (index, &(start, end)) in ranges.iter().enumerate() {
        if index != 0 {
            output.push(',');
        }
        output.push('[');
        output.push_str(&start.to_string());
        output.push(',');
        output.push_str(&end.to_string());
        output.push(']');
    }
    output.push_str("]}\n");
    Ok(output)
}

fn main() {
    let output = match build_output() {
        Ok(output) => output,
        Err(()) => {
            let stderr = io::stderr();
            let mut error_output = stderr.lock();
            let _ = error_output.write_all(b"error: invalid input\n");
            let _ = error_output.flush();
            std::process::exit(2);
        }
    };

    let stdout = io::stdout();
    let mut output_stream = stdout.lock();
    if output_stream.write_all(output.as_bytes()).is_err()
        || output_stream.flush().is_err()
    {
        std::process::exit(2);
    }
}
