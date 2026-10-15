use std::io::{self, Read, Write};

fn invalid() -> ! {
    let mut stderr = io::stderr().lock();
    let _ = stderr.write_all(b"error: invalid input\n");
    let _ = stderr.flush();
    std::process::exit(2);
}

fn main() {
    if std::env::args_os().skip(1).next().is_some() {
        invalid();
    }

    let mut buffer = [0u8; 65_537];
    let mut used = 0usize;
    {
        let mut stdin = io::stdin().lock();
        loop {
            match stdin.read(&mut buffer[used..]) {
                Ok(0) => break,
                Ok(n) => {
                    used += n;
                    if used > 65_536 {
                        invalid();
                    }
                }
                Err(e) if e.kind() == io::ErrorKind::Interrupted => continue,
                Err(_) => invalid(),
            }
        }
    }

    let text = match std::str::from_utf8(&buffer[..used]) {
        Ok(text) => text,
        Err(_) => invalid(),
    };
    if text.starts_with('\u{feff}') || text.as_bytes().contains(&b'\r') {
        invalid();
    }

    // Validate every retained line before counting any equals signs.
    let mut lines: Vec<&str> = Vec::new();
    for line in text.split('\n') {
        if line.is_empty() {
            continue;
        }
        if line.len() > 256 || lines.len() >= 100 {
            invalid();
        }
        lines.push(line);
    }

    let mut output = String::from("{\"counts\":[");
    for (index, line) in lines.iter().enumerate() {
        if index != 0 {
            output.push(',');
        }
        let count = line.bytes().filter(|&byte| byte == b'=').count();
        output.push_str(&count.to_string());
    }
    output.push_str("]}\n");

    let mut stdout = io::stdout().lock();
    if stdout.write_all(output.as_bytes()).is_err() || stdout.flush().is_err() {
        std::process::exit(2);
    }
}
