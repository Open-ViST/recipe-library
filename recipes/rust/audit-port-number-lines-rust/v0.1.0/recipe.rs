use std::io::{self, Read, Write};

fn invalid_input() -> ! {
    let stderr = io::stderr();
    let mut err = stderr.lock();
    let _ = err.write_all(b"error: invalid input\n");
    let _ = err.flush();
    std::process::exit(2);
}

fn read_and_validate() -> Result<Vec<u16>, ()> {
    let stdin = io::stdin();
    let mut reader = stdin.lock().take(65537);
    let mut bytes = Vec::new();
    reader.read_to_end(&mut bytes).map_err(|_| ())?;

    if bytes.len() > 65536 || bytes.starts_with(&[0xEF, 0xBB, 0xBF]) {
        return Err(());
    }
    let text = std::str::from_utf8(&bytes).map_err(|_| ())?;
    let mut ports = Vec::new();

    for line in text.split('\n') {
        if line.is_empty() {
            continue;
        }
        if ports.len() == 100 {
            return Err(());
        }
        let digits = line.as_bytes();
        if digits.len() > 5
            || !digits.iter().all(|b| b.is_ascii_digit())
            || (digits.len() > 1 && digits[0] == b'0')
        {
            return Err(());
        }
        let port = line.parse::<u16>().map_err(|_| ())?;
        ports.push(port);
    }

    ports.sort_unstable();
    ports.dedup();
    Ok(ports)
}

fn main() {
    if std::env::args_os().skip(1).next().is_some() {
        invalid_input();
    }

    let ports = match read_and_validate() {
        Ok(ports) => ports,
        Err(()) => invalid_input(),
    };

    let mut output = String::from("{\"ports\":[");
    for (index, port) in ports.iter().enumerate() {
        if index != 0 {
            output.push(',');
        }
        output.push_str(&port.to_string());
    }
    output.push_str("]}\n");

    let stdout = io::stdout();
    let mut out = stdout.lock();
    if out.write_all(output.as_bytes()).is_err() || out.flush().is_err() {
        std::process::exit(2);
    }
}
