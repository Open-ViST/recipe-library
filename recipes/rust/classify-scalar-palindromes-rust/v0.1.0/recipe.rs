use std::io::{self, Read, Write};
use std::str;

fn prepare_output() -> Result<String, ()> {
    if std::env::args_os().skip(1).next().is_some() {
        return Err(());
    }

    let stdin = io::stdin();
    let mut reader = stdin.lock().take(65_537);
    let mut bytes = Vec::new();
    reader.read_to_end(&mut bytes).map_err(|_| ())?;

    if bytes.len() > 65_536 {
        return Err(());
    }

    let text = str::from_utf8(&bytes).map_err(|_| ())?;
    if text.starts_with('\u{FEFF}') || text.contains('\r') {
        return Err(());
    }

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

    // All input validation is complete before classification begins.
    let mut output = String::from("{\"palindromes\":[");
    for (index, line) in lines.iter().enumerate() {
        if index != 0 {
            output.push(',');
        }
        let palindrome = line.chars().eq(line.chars().rev());
        output.push_str(if palindrome { "true" } else { "false" });
    }
    output.push_str("]}\n");
    Ok(output)
}

fn main() {
    match prepare_output() {
        Ok(output) => {
            let stdout = io::stdout();
            let mut writer = stdout.lock();
            if writer.write_all(output.as_bytes()).is_err()
                || writer.flush().is_err()
            {
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
