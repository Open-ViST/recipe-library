use std::io::{self, ErrorKind, Read, Write};

fn invalid_input() -> ! {
    let _ = io::stderr().lock().write_all(b"error: invalid input\n");
    std::process::exit(2);
}

fn read_and_count() -> Result<[usize; 4], ()> {
    let mut buffer = [0u8; 65537];
    let mut length = 0usize;
    let stdin = io::stdin();
    let mut input = stdin.lock();

    loop {
        match input.read(&mut buffer[length..]) {
            Ok(0) => break,
            Ok(n) => {
                length += n;
                if length > 65536 {
                    return Err(());
                }
            }
            Err(error) if error.kind() == ErrorKind::Interrupted => continue,
            Err(_) => return Err(()),
        }
    }

    let bytes = &buffer[..length];
    let text = std::str::from_utf8(bytes).map_err(|_| ())?;
    if bytes.starts_with(&[0xEF, 0xBB, 0xBF]) || !text.is_ascii() {
        return Err(());
    }

    let mut counts = [0usize; 4];
    for &byte in bytes {
        let class = match byte {
            b'A'..=b'Z' | b'a'..=b'z' => 0,
            b'0'..=b'9' => 1,
            9 | 10 | 12 | 13 | 32 => 2,
            _ => 3,
        };
        counts[class] += 1;
    }
    Ok(counts)
}

fn main() {
    if std::env::args_os().nth(1).is_some() {
        invalid_input();
    }

    let counts = match read_and_count() {
        Ok(counts) => counts,
        Err(()) => invalid_input(),
    };

    let stdout = io::stdout();
    let mut output = stdout.lock();
    let result = writeln!(
        output,
        "{{\"letters\":{},\"digits\":{},\"whitespace\":{},\"other\":{}}}",
        counts[0], counts[1], counts[2], counts[3]
    );
    if result.is_err() || output.flush().is_err() {
        std::process::exit(2);
    }
}
