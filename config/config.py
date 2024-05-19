from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DOCSABOT",
    settings_files=["settings.yaml", ".secrets.yaml"],
    merge_enabled=True,
)