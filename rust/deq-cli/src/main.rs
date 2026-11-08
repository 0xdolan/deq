//! `deq` CLI. Placeholder created in Phase 0; the full interface (PRD §8.9) lands in Phase 6.

use std::process::ExitCode;

fn run(args: &[String]) -> Result<String, String> {
    match args.first().map(String::as_str) {
        Some("--version" | "-V") => Ok(format!("deq {}", deq_shapes::VERSION)),
        Some("--help" | "-h") | None => Ok("Usage: deq [--version | --help]".to_owned()),
        Some(other) => Err(format!("unknown argument: {other}")),
    }
}

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    match run(&args) {
        Ok(out) => {
            println!("{out}");
            ExitCode::SUCCESS
        }
        Err(err) => {
            eprintln!("error: {err}");
            ExitCode::from(2)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::run;

    #[test]
    fn prints_version() {
        assert_eq!(
            run(&["--version".into()]),
            Ok(format!("deq {}", deq_shapes::VERSION))
        );
    }

    #[test]
    fn help_is_default() {
        assert!(run(&[]).is_ok_and(|s| s.starts_with("Usage")));
    }

    #[test]
    fn rejects_unknown_args() {
        assert!(run(&["--nope".into()]).is_err());
    }
}
