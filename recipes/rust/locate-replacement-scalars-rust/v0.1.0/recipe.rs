use std::io::{self, ErrorKind, Read, Write};

fn prepare_output() -> Result<String, ()> {
    if std::env::args_os().skip(1).next().is_some() {
        return Err(());
    }

    // Read at most 65537 bytes, using the extra byte to detect oversize input.
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
                Err(error) if error.kind() == ErrorKind::Interrupted => continue,
                Err(_) => return Err(()),
            }
        }
    }

    let text = std::str::from_utf8(&buffer[..used]).map_err(|_| ())?;
    if text.starts_with('\u{FEFF}') || text.contains('\r') {
        return Err(());
    }

    // Complete all line validation before inspecting replacement markers.
    let mut count = 0usize;
    for line in text.split('\n') {
        if line.is_empty() {
            continue;
        }
        count += 1;
        if count > 100 || line.len() > 256 {
            return Err(());
        }
    }

    let mut output = String::from("{\"positions\":[");
    let mut retained_index = 0usize;
    let mut first = true;
    for line in text.split('\n') {
        if line.is_empty() {
            continue;
        }
        retained_index += 1;
        if line.contains('\u{FFFD}') {
            if !first {
                output.push(',');
            }
            first = false;
            output.push_str(&retained_index.to_string());
        }
    }
    output.push_str("]}\n");
    Ok(output)
}

fn main() {
    match prepare_output() {
        Ok(output) => {
            let stdout = io::stdout();
            if stdout.lock().write_all(output.as_bytes()).is_err() {
                std::process::exit(2);
            }
        }
        Err(()) => {
            let stderr = io::stderr();
            let _ = stderr.lock().write_all(b"error: invalid input\n");
            std::process::exit(2);
        }
    }
}
