use std::io::{self, Read, Write};

fn prepare_output() -> Result<String, ()> {
    if std::env::args_os().nth(1).is_some() {
        return Err(());
    }

    let stdin = io::stdin();
    let mut reader = stdin.lock().take(65_537);
    let mut bytes = Vec::with_capacity(65_537);
    reader.read_to_end(&mut bytes).map_err(|_| ())?;
    if bytes.len() > 65_536 {
        return Err(());
    }

    let text = std::str::from_utf8(&bytes).map_err(|_| ())?;
    if text.starts_with('\u{feff}') || text.contains('\r') {
        return Err(());
    }

    // Validate every retained line before comparing or grouping any lines.
    let mut lines: Vec<&str> = Vec::with_capacity(100);
    for line in text.split('\n') {
        if line.is_empty() {
            continue;
        }
        if line.len() > 256 || lines.len() >= 100 {
            return Err(());
        }
        lines.push(line);
    }

    let mut runs: Vec<usize> = Vec::with_capacity(100);
    let mut previous: Option<&str> = None;
    let mut length = 0usize;
    for line in lines {
        if previous == Some(line) {
            length += 1;
        } else {
            if length != 0 {
                runs.push(length);
            }
            previous = Some(line);
            length = 1;
        }
    }
    if length != 0 {
        runs.push(length);
    }

    let mut output = String::with_capacity(512);
    output.push_str("{\"runs\":[");
    for (index, length) in runs.iter().enumerate() {
        if index != 0 {
            output.push(',');
        }
        output.push_str(&length.to_string());
    }
    output.push_str("]}\n");
    Ok(output)
}

fn main() {
    match prepare_output() {
        Ok(output) => {
            let stdout = io::stdout();
            let mut writer = stdout.lock();
            if writer.write_all(output.as_bytes())
                .and_then(|_| writer.flush())
                .is_err()
            {
                std::process::exit(1);
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
