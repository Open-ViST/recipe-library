use std::io::{self, Read, Write};

fn invalid_input() -> ! {
    let _ = io::stderr().lock().write_all(b"error: invalid input\n");
    std::process::exit(2);
}

fn prepare_output() -> Result<String, ()> {
    if std::env::args_os().skip(1).next().is_some() {
        return Err(());
    }

    // Read at most 65537 bytes, including the oversize-detection byte.
    let mut buffer = vec![0u8; 65_537];
    let mut used = 0usize;
    {
        let stdin = io::stdin();
        let mut input = stdin.lock();
        loop {
            match input.read(&mut buffer[used..]) {
                Ok(0) => break,
                Ok(n) => {
                    used += n;
                    if used == buffer.len() {
                        return Err(());
                    }
                }
                Err(e) if e.kind() == io::ErrorKind::Interrupted => continue,
                Err(_) => return Err(()),
            }
        }
    }

    let text = std::str::from_utf8(&buffer[..used]).map_err(|_| ())?;
    if text.starts_with('\u{FEFF}') || text.as_bytes().contains(&b'\r') {
        return Err(());
    }

    // Finish all line-contract validation before classifying any line.
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

    let mut output = String::from("{\"positions\":[");
    let mut first = true;
    for (index, line) in lines.iter().enumerate() {
        if line.as_bytes().iter().any(|&byte| byte < 32 || byte == 127) {
            if !first {
                output.push(',');
            }
            first = false;
            output.push_str(&(index + 1).to_string());
        }
    }
    output.push_str("]}\n");
    Ok(output)
}

fn main() {
    let output = match prepare_output() {
        Ok(output) => output,
        Err(()) => invalid_input(),
    };

    let stdout = io::stdout();
    let mut destination = stdout.lock();
    if destination.write_all(output.as_bytes()).is_err() {
        std::process::exit(2);
    }
    if destination.flush().is_err() {
        std::process::exit(2);
    }
}
