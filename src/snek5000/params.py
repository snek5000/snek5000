"""Runtime parameters
=====================
Scripting interface for Nek5000 :ref:`parameter file <nek:case_files_par>`.

"""
import textwrap
from configparser import ConfigParser
from io import StringIO
from math import nan
from pathlib import Path
from ast import literal_eval
import json
from warnings import warn

from fluidsim_core.params import Parameters as _Parameters
from inflection import camelize, underscore

from .solvers import get_solver_short_name, import_cls_simul

literal_python2nek = {
    nan: "<real>",
    "nan": "nan",
    "None": "none",
    "True": "yes",
    "False": "no",
}
literal_nek2python = {v: k for k, v in literal_python2nek.items()}
literal_prune = ("<real>", "", "nan")

filename_map_user_params = "map_user_params.json"


def _prepare_nek_value(value):
    # Convert to string to avoid hash collisions
    # hash(1) == hash(True)
    literal = str(value) if value is not nan else nan
    if literal in literal_python2nek:
        value = literal_python2nek[literal]
    return value


def camelcase(value):
    return camelize(str(value).lower(), uppercase_first_letter=False)


def _check_user_param(idx):
    if idx > 20:
        raise ValueError(f"userParam {idx = } > 20")


def _as_python_value(value):
    if value in literal_nek2python:
        value = literal_nek2python[value]
    try:
        return literal_eval(value)

    except (SyntaxError, ValueError):
        return value


def load_params(path_dir="."):
    """Load a :class:`snek5000.params.Parameters` instance from `path_dir`.

    Parameters
    ----------
    path_dir : str or path-like
        Path to a simulation directory.

    Returns
    -------
    params: :class:`snek5000.params.Parameters`

    """
    path_dir = Path(path_dir)
    short_name = get_solver_short_name(path_dir)
    Simul = import_cls_simul(short_name)

    return Simul.load_params_from_file(
        path_xml=path_dir / "params_simul.xml", path_par=path_dir / f"{short_name}.par"
    )


class Parameters(_Parameters):
    """Container for reading, modifying and writing :ref:`par files <nek:case_files_par>`.

    :param tag: A string representing name of case files (for example: provide
                 ``"abl"`` for files like ``abl.usr, abl.par`` etc).

    :todo: Consolidate the logic of param to par file syncing in two methods!
           More tests to see if it works.

    """

    @classmethod
    def _load_params_simul(cls, path=None):
        """Alias for :func:`load_params`"""
        return load_params(path or Path.cwd())

    def __init__(self, *args, **kwargs):
        comments = ("#",)
        self._set_internal_attr(
            "_par_file",
            ConfigParser(comment_prefixes=comments, inline_comment_prefixes=comments),
        )
        # Only enabled parameters would be written into par file
        self._set_internal_attr("_enabled", True)
        # User parameters sections should begin with an underscore
        self._set_internal_attr("_user", True)

        super().__init__(*args, **kwargs)

        # Like in Python Nek5000's par files are case insensitive.
        # However for consistency, case sensitivity is enforced:
        self._par_file.optionxform = str

    def _make_dict_attribs(self):
        d = super()._make_dict_attribs()
        # Append internal attributes
        d.update({"_enabled": self._enabled, "_user": self._user})
        if hasattr(self, "_recorded_user_params"):
            d["_recorded_user_params"] = self._recorded_user_params
        return d

    def __update_par_section(
        self, section_name, section_dict, has_to_prune_literals=True
    ):
        """Updates a section of the ``par_file`` object from a dictionary."""
        par = self._par_file

        # Start with underscore if it is a user section
        section_name_par = "_" if section_dict["_user"] else ""
        section_name_par += section_name.upper().lstrip("_")

        if section_name_par not in par.sections():
            par.add_section(section_name_par)

        if "_recorded_user_params" in section_dict:
            recorded_user_params = section_dict.pop("_recorded_user_params")
        else:
            recorded_user_params = False

        for option, value in section_dict.items():
            value = _prepare_nek_value(value)

            if has_to_prune_literals and value in literal_prune:
                continue

            # Make everything consistent where values refer to option names
            # if option in ("stop_at", "write_control"):
            if str(value) in section_dict:
                value = camelcase(value)

            par.set(section_name_par, camelcase(option), str(value))

        # _recorded_user_params -> userParam%%
        if not recorded_user_params:
            return
        params = self._parent
        if self._tag != "nek" or params._tag != "params":
            raise RuntimeError(
                "_recorded_user_params should only be in params.nek.general"
            )
        for idx_uparam in sorted(recorded_user_params.keys()):
            tag = recorded_user_params[idx_uparam]
            _check_user_param(idx_uparam)
            value = _prepare_nek_value(params[tag])
            par.set(
                section_name_par,
                f"userParam{idx_uparam:02d}",
                str(value),
            )

    def _sync_par(self, has_to_prune_literals=True, keep_all_sections=False):
        """Sync values in param children and attributes to ``self._par_file``
        object.

        """
        if self._tag_children:
            data = [
                (child, getattr(self, child)._make_dict_tree())
                for child in self._tag_children
            ]
        else:
            # No children
            data = [(self._tag, self._make_dict_attribs())]

        for child, d in data:
            section_name = child.upper()
            self.__update_par_section(
                section_name, d, has_to_prune_literals=has_to_prune_literals
            )

        self.__tidy_par(keep_all_sections)

    def __tidy_par(self, keep_all_sections=False):
        """Remove internal attributes and disabled sections from par file."""
        par = self._par_file
        for section_name in par.sections():
            par.remove_option(section_name, "_user")

            if keep_all_sections:
                enabled = True
            else:
                enabled = par.getboolean(section_name, "_enabled")
            if enabled:
                par.remove_option(section_name, "_enabled")
            else:
                par.remove_section(section_name)

    def _autodoc_par(self, indent=0):
        """Autodoc a code block with ``ini`` syntax and set docstring."""
        self._sync_par(has_to_prune_literals=False, keep_all_sections=True)
        docstring = "\n.. code-block:: ini\n\n"
        with StringIO() as output:
            self._par_file.write(output)
            ini = output.getvalue()

        docstring += textwrap.indent(ini, "   ")

        if ini:
            self._set_doc(self._doc + textwrap.indent(docstring, " " * indent))

    def _record_nek_user_params(self, nek_params_keys, overwrite=False):
        """Record some Nek user parameters

        Examples
        --------

        >>> params._record_nek_user_params({"prandtl": 2, "rayleigh": 3})
        >>> params.output.history_points._record_nek_user_params({"write_interval": 4})

        This is going to set or modify the internal attribute
        ``params.nek.general._recorded_user_params`` to ``{2: "prandtl", 3:
        "rayleigh", 4: "output.other.write_interval"}``.

        This attribute is then used to write the ``[GENERAL]`` section of the
        .par file.

        Note that this attribute is only for ``params.nek.general`` and should
        never be set for other parameter children.
        """
        # we need to find where is self in the tree compared to `params`
        current = self
        parent = current._parent
        tag = current._tag
        path = tag

        while not (parent is None and tag == "params") and not (
            parent._tag == "info_simul" and tag == "params"
        ):
            current = parent
            parent = current._parent
            tag = current._tag
            path = f"{tag}.{path}"

        params = current
        assert params._tag == "params"

        # path relative to params
        path = path[len("params") :]
        if path.startswith("."):
            path = path[1:]

        if path:
            path = path + "."

        user_params = {}
        for name, key in nek_params_keys.items():
            user_params[key] = f"{path}{name}"

        general = params.nek.general
        if not hasattr(general, "_recorded_user_params"):
            general._set_internal_attr("_recorded_user_params", {})

        if overwrite:
            general._recorded_user_params.update(user_params)
            return

        for key, value in user_params.items():
            if key in general._recorded_user_params:
                raise ValueError(
                    f"{key = } already used for user parameter "
                    f"{general._recorded_user_params[key]}"
                )
            general._recorded_user_params[key] = value

    def _save_as_xml(self, path_file=None, comment=None, find_new_name=False):
        try:
            user_params = self.nek.general._recorded_user_params
        except AttributeError:
            pass
        else:
            if path_file is None:
                path_dir = Path.cwd()
            else:
                path_dir = Path(path_file).parent
            _save_recorded_user_params(user_params, path_dir)

        return super()._save_as_xml(
            path_file=path_file, comment=comment, find_new_name=find_new_name
        )


def _save_recorded_user_params(user_params, path_dir):
    with open(path_dir / filename_map_user_params, "w") as file:
        json.dump(user_params, file)


def _load_recorded_user_params(path):
    with open(path) as file:
        tmp = json.load(file)
    return {int(key): value for key, value in tmp.items()}


def _check_and_get_params_nek(params, path):
    if not isinstance(path, Path):
        raise TypeError

    if not isinstance(params, Parameters):
        raise TypeError
    if params._tag != "params":
        raise ValueError(f'{params._tag = } != "params"')

    if params.nek._tag != "nek":
        raise RuntimeError(f'{params.nek._tag =} != "nek"')
    return params.nek


def _save_par_file(params, path, mode="w"):
    nek = _check_and_get_params_nek(params, path)
    nek._sync_par()
    with open(path, mode) as fp:
        nek._par_file.write(fp)

    if hasattr(nek.general, "_recorded_user_params"):
        _save_recorded_user_params(nek.general._recorded_user_params, path.parent)


def _complete_params_from_par_file(params, path):
    nek = _check_and_get_params_nek(params, path)
    nek._par_file.read(path)

    recorded_user_params_path = path.with_name(filename_map_user_params)
    if recorded_user_params_path.exists():
        recorded_user_params = _load_recorded_user_params(recorded_user_params_path)
    elif hasattr(nek.general, "_recorded_user_params"):
        recorded_user_params = nek.general._recorded_user_params
    else:
        recorded_user_params = {}

    for section in nek._par_file.sections():
        params_child = getattr(nek, section.lower().lstrip("_"))

        for option, value in nek._par_file.items(section):
            value = _as_python_value(value)

            # userParam%% -> user_params
            if option.lower().startswith("userparam"):
                idx_uparam = int(option[-2:])
                _check_user_param(idx_uparam)
                if idx_uparam not in recorded_user_params:
                    warn(
                        f"{idx_uparam = } not in {recorded_user_params = } so we"
                        "cannot update the right parameter in the object `params`."
                        "It might be because you load a simulation done with "
                        "an old snek5000 (< 0.8), or it might be a bug :-)"
                    )
                tag = recorded_user_params[idx_uparam]
                # set the corresponding parameter
                params[tag] = value
            else:
                attrib = underscore(option)
                setattr(params_child, attrib, value)


def _complete_params_from_xml_file(params, path_xml):
    params._load_from_xml_file(str(path_xml))
    nek = _check_and_get_params_nek(params, path_xml)
    path_recorded_user_params = Path(path_xml).parent / filename_map_user_params
    if path_recorded_user_params.exists():
        nek.general._set_internal_attr(
            "_recorded_user_params",
            _load_recorded_user_params(path_recorded_user_params),
        )


create_params = Parameters._create_params
