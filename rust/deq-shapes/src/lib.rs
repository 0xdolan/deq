//! `deq-shapes`: Deq shapes for Rust.
//!
//! Placeholder created in Phase 0. The real implementation lands in Phase 6 (see PRD §15).

/// The crate name as published on crates.io.
pub const CRATE_NAME: &str = env!("CARGO_PKG_NAME");

/// The crate version (shared, unified Deq version).
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn crate_name_matches() {
        assert_eq!(CRATE_NAME, "deq-shapes");
    }

    #[test]
    fn version_is_semver() {
        let parts: Vec<&str> = VERSION.split('.').collect();
        assert_eq!(parts.len(), 3);
        assert!(parts.iter().all(|p| p.chars().all(|c| c.is_ascii_digit())));
    }
}
