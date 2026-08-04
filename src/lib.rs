pub mod ext;
pub use ext::calculate_differences::calculate_differences;
pub use ext::say_hello::say_hello;
use pyo3::prelude::*;

#[pyfunction]
fn hello_from_bin() -> String {
    "Hello from jcutils!".to_string()
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
/// `gil_used = false` declares this module is thread-safe and supports
/// free-threaded Python (PEP 703, Python 3.13t+).
#[pymodule(gil_used = false)]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello_from_bin, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_differences, m)?)?;
    m.add_function(wrap_pyfunction!(say_hello, m)?)?;
    Ok(())
}
