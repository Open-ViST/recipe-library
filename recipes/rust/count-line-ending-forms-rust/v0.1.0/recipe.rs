use std::io::{self, ErrorKind, Read, Write};

fn invalid() -> ! {
    let _ = io::stderr().lock().write_all(b"error: invalid input\n");
    std::process::exit(2);
}

fn main() {
    if std::env::args_os().skip(1).next().is_some() {
        invalid();
    }

    let mut buffer = [0u8; 65_537];
    let mut used = 0usize;
    {
        let stdin = io::stdin();
        let mut input = stdin.lock();
        loop {
            if used == buffer.len() {
                invalid();
            }
            match input.read(&mut buffer[used..]) {
                Ok(0) => break,
                Ok(n) => used += n,
                Err(e) if e.kind() == ErrorKind::Interrupted => continue,
                Err(_) => invalid(),
            }
        }
    }

    let bytes = &buffer[..used];
    if bytes.starts_with(&[0xEF, 0xBB, 0xBF])
        || std::str::from_utf8(bytes).is_err()
    {
        invalid();
    }

    let mut lf = 0usize;
    let mut crlf = 0usize;
    let mut cr = 0usize;
    let mut i = 0usize;
    while i < bytes.len() {
        match bytes[i] {
            b'\r' => {
                if i + 1 < bytes.len() && bytes[i + 1] == b'\n' {
                    crlf += 1;
                    i += 2;
                } else {
                    cr += 1;
                    i += 1;
                }
            }
            b'\n' => {
                lf += 1;
                i += 1;
            }
            _ => i += 1,
        }
    }

    let stdout = io::stdout();
    let mut output = stdout.lock();
    if writeln!(output, "{{\"lf\":{},\"crlf\":{},\"cr\":{}}}", lf, crlf, crlf.wrapping_sub(crlf) + cr).is_err()
        || output.flush().is_err()
    {
        std::process::exit(2);
    }
}
