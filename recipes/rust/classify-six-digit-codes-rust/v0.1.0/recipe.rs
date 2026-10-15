use std::io::{self, Read, Write};
use std::str;

fn invalid() -> ! {
    let stderr = io::stderr();
    let mut err = stderr.lock();
    let _ = err.write_all(b"error: invalid input\n");
    let _ = err.flush();
    std::process::exit(2);
}

fn main() {
    if std::env::args_os().skip(1).next().is_some() {
        invalid();
    }

    let mut buffer = vec![0u8; 65537];
    let mut used = 0usize;
    {
        let stdin = io::stdin();
        let mut input = stdin.lock();
        while used < buffer.len() {
            match input.read(&mut buffer[used..]) {
                Ok(0) => break,
                Ok(n) => used += n,
                Err(e) if e.kind() == io::ErrorKind::Interrupted => continue,
                Err(_) => invalid(),
            }
        }
    }
    if used > 65536 {
        invalid();
    }

    let text = match str::from_utf8(&buffer[..used]) {
        Ok(text) => text,
        Err(_) => invalid(),
    };
    if text.starts_with('\u{feff}') || text.as_bytes().contains(&b'\r') {
        invalid();
    }

    let mut lines: Vec<&str> = Vec::with_capacity(100);
    for line in text.split('\n') {
        if line.is_empty() {
            continue;
        }
        if line.len() > 256 || lines.len() >= 100 {
            invalid();
        }
        lines.push(line);
    }

    // All input validation is complete before classification or output.
    let mut output = String::with_capacity(612);
    output.push_str("{\"valid\":[");
    for (index, line) in lines.iter().enumerate() {
        if index != 0 {
            output.push(',');
        }
        let bytes = line.as_bytes();
        let valid = bytes.len() == 6 && bytes.iter().all(|b| b.is_ascii_digit());
        output.push_str(if valid { "true" } else { "false" });
    }
    output.push_str("]}\n");

    let stdout = io::stdout();
    let mut out = stdout.lock();
    if out.write_all(output.as_bytes()).is_err() || out.flush().is_err() {
        std::process::exit(1);
    }
}
