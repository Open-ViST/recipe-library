use std::io::{self, Read, Write};

fn invalid_input() -> ! {
    let _ = io::stderr().lock().write_all(b"error: invalid input\n");
    std::process::exit(2);
}

fn validated_output() -> Result<String, ()> {
    let stdin = io::stdin();
    let mut reader = stdin.lock().take(65_537);
    let mut bytes = Vec::with_capacity(65_537);
    reader.read_to_end(&mut bytes).map_err(|_| ())?;

    if bytes.len() > 65_536
        || bytes.starts_with(&[0xEF, 0xBB, 0xBF])
        || bytes.contains(&b'\r')
    {
        return Err(());
    }
    let text = std::str::from_utf8(&bytes).map_err(|_| ())?;

    // Finish all line-limit validation before comparing or grouping lines.
    let mut lines: Vec<&str> = Vec::new();
    for line in text.split('\n') {
        if line.is_empty() {
            continue;
        }
        if line.len() > 256 || lines.len() >= 100 {
            return Err(());
        }
        lines.push(line);
    }

    let mut visited = [false; 100];
    let mut groups: Vec<Vec<usize>> = Vec::new();
    for i in 0..lines.len() {
        if visited[i] {
            continue;
        }
        let mut positions = Vec::new();
        for j in i..lines.len() {
            if lines[j] == lines[i] {
                visited[j] = true;
                positions.push(j + 1);
            }
        }
        if positions.len() >= 2 {
            groups.push(positions);
        }
    }

    let mut output = String::from("{\"groups\":[");
    for (group_index, group) in groups.iter().enumerate() {
        if group_index != 0 {
            output.push(',');
        }
        output.push('[');
        for (position_index, position) in group.iter().enumerate() {
            if position_index != 0 {
                output.push(',');
            }
            output.push_str(&position.to_string());
        }
        output.push(']');
    }
    output.push_str("]}\n");
    Ok(output)
}

fn main() {
    if std::env::args_os().nth(1).is_some() {
        invalid_input();
    }

    let output = match validated_output() {
        Ok(output) => output,
        Err(()) => invalid_input(),
    };

    let stdout = io::stdout();
    let mut writer = stdout.lock();
    if writer.write_all(output.as_bytes()).is_err() || writer.flush().is_err() {
        std::process::exit(1);
    }
}
