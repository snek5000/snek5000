import nox

# From running `pip index versions snakemake`
snakemake_versions = """7.18.2, 7.18.1, 7.18.0, 7.17.1, 7.17.0, 7.16.2, 7.16.1, 7.16.0, 7.15.2, 7.15.1, 7.15.0, 7.14.2, 7.14.1, 7.14.0, 7.13.0, 7.12.1, 7.12.0, 7.11.0, 7.10.0, 7.9.0, 7.8.5, 7.8.3, 7.8.2, 7.8.1, 7.8.0, 7.7.0, 7.6.2, 7.6.1, 7.6.0, 7.5.0, 7.4.0, 7.3.8, 7.3.7, 7.3.6, 7.3.5, 7.3.4, 7.3.3, 7.3.2, 7.3.1, 7.3.0, 7.2.1, 7.2.0, 7.1.1, 7.1.0, 7.0.4, 7.0.3, 7.0.2, 7.0.1, 7.0.0, 6.15.5, 6.15.4, 6.15.3, 6.15.2, 6.15.1, 6.15.0, 6.14.0, 6.13.1, 6.13.0, 6.12.3, 6.12.2, 6.12.1, 6.12.0, 6.11.1, 6.11.0, 6.10.0, 6.9.1, 6.9.0, 6.8.2, 6.8.1, 6.8.0, 6.7.0, 6.6.1, 6.6.0, 6.5.5, 6.5.3, 6.5.2, 6.5.1, 6.5.0""".split(
    ", "
)
snakemake_old_versions = """6.4.1, 6.4.0, 6.3.0, 6.2.1, 6.2.0, 6.1.2, 6.1.1, 6.1.0, 6.0.5, 6.0.4, 6.0.3, 6.0.2, 6.0.1, 6.0.0""".split(
    ", "
)
snakemake_minor_versions = [ver for ver in snakemake_versions if ver.endswith(".0")]
snakemake_latest_versions = snakemake_versions[:11]


@nox.session
@nox.parametrize("snakemake", snakemake_latest_versions)
def tests(session, snakemake):
    session.install("pytest", f"snakemake=={snakemake}")
    session.run("pytest", "--tb=short", "--show-capture=stdout", "run.py")
