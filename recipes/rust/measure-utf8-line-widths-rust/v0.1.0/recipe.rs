use std::io::{self, Read, Write};

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

    let mut input = Vec::with_capacity(65_537);
    {
        let stdin = io::stdin();
        let mut reader = stdin.lock().take(65_537);
        if reader.read_to_end(&mut input).is_err() {
            invalid();
        }
    }
    if input.len() > 65_536 {
        invalid();
    }

    let text = match std::str::from_utf8(&input) {
        Ok(text) => text,
        Err(_) => invalid(),
    };
    if text.starts_with('\u{feff}') || text.contains('\r') {
        invalid();
    }

    let mut lines: Vec<&str> = Vec::with_capacity(100);
    for line in text.split('\n') {
        if line.is_empty() {
            continue;
        }
        if line.len() > 256 || lines.len() == 100 {
            invalid();
        }
        lines.push(line);
    }

    // All input validation is complete before constructing successful output.
    let mut output = String::from("{\"widths\":[");
    for (index, line) in lines.iter().enumerate() {
        if index != 0 {
            output.push(',');
        }
        output.push_str("{\"bytes\":");
        output.push_str(&line.len().to_string());
        output.push_str(",\"scalars\":");
        output.push_str(&line.chars().count().to_string());
        output.push('}');
    }
    output.push_str("]}\n");

    let stdout = io::stdout();
    let mut out = stdout.lock();
    if out.write_all(output.as_bytes()).is_err() || out.flush().is_err() {
        std::process::exit(1);
    }
}
