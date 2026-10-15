use std::io::{self, Read, Write};

fn prepare_output() -> Result<String, ()> {
    if std::env::args_os().skip(1).next().is_some() {
        return Err(());
    }

    let mut input = Vec::with_capacity(65_537);
    {
        let stdin = io::stdin();
        let mut reader = stdin.lock().take(65_537);
        reader.read_to_end(&mut input).map_err(|_| ())?;
    }
    if input.len() > 65_536 {
        return Err(());
    }

    let text = std::str::from_utf8(&input).map_err(|_| ())?;
    if text.starts_with('\u{feff}') || input.contains(&b'\r') {
        return Err(());
    }

    // Validate and retain all lines before classifying any spelling.
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

    let mut output = String::with_capacity(640);
    output.push_str("{\"valid\":[");
    for (index, line) in lines.iter().enumerate() {
        if index != 0 {
            output.push(',');
        }
        let valid = line.len() == 64
            && line.bytes().all(|b| matches!(b, b'0'..=b'9' | b'a'..=b'f'));
        output.push_str(if valid { "true" } else { "false" });
    }
    output.push_str("]}\n");
    Ok(output)
}

fn main() {
    match prepare_output() {
        Ok(output) => {
            let stdout = io::stdout();
            let mut writer = stdout.lock();
            if writer.write_all(output.as_bytes()).is_err() || writer.flush().is_err() {
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
