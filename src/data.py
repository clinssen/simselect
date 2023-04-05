import yaml
from pathlib import Path
def get_files(dirname):
    """
    Return
    Args:
        dirname: Path
            directory containing the yaml files

    Yields:
        Filenames
    """
    for fname in sorted(dirname.glob('*.yaml')):
        if not fname.name == 'simtools.yaml':  # hardcoded exception
            yield fname.resolve()

def string_to_list(s):
    """
    Helper function to convert a string to a list, e.g. `'A, B'` to `['A', 'B']`
    """
    if s:
        return sorted(l.strip() for l in s.split(","))
    else:
        return []

def parse_file(filename):
    """
    Parse a yaml file and return content as dictionary
    Args:
        filename: Path
            The name of the yaml file to parse

    Returns:
        A dictionary with the content of the yaml file
    """
    with open(filename) as f:
        content = yaml.safe_load(f)
        content_dict = {}
        for element in content:
            if not isinstance(element, dict):
                print(f"Ignoring top-level element of type {type(element)}")
                continue
            key, value = list(element.items())[0]
            content_dict[key] = value
    # Normalize the standard fields

    # Operating System
    assert "operating_system" in content_dict, "no operating_system entry"
    assert isinstance(content_dict["operating_system"], list), "operating_system is not a list"
    if len(content_dict["operating_system"]) and not isinstance(content_dict["operating_system"][0], str):
        os_support = content_dict["operating_system"]
        content_dict["operating_system"] = sorted(os for os_support_dict in os_support
                                                  for os, supported in os_support_dict.items()
                                                  if supported)

    # Biological level
    assert "biological_level" in content_dict, "no biological level"
    content_dict["biological_level"] = string_to_list(content_dict["biological_level"])

    # Computing scale
    assert "computing_scale" in content_dict, "no computing scale"
    content_dict["computing_scale"] = string_to_list(content_dict["computing_scale"])

    # interface language
    assert "interface_language" in content_dict, "no interface language"
    content_dict["interface_language"] = string_to_list(content_dict["interface_language"])

    # Model description language
    assert "model__description_language" in content_dict, "no model description language"
    content_dict["model__description_language"] = string_to_list(content_dict["model__description_language"])
    return content_dict


def parse_files(dirname=Path(__file__).parent / '..' / 'simtools'):
    simulators = {}
    for f in get_files(dirname):
        try:
            content = parse_file(f)
        except Exception as ex:
            print(f"Error: {ex}")
            continue
        simulators[content["name"]] = content
    return simulators


def unique_entries(simulators, fields=("operating_system",
                                       "biological_level",
                                       "computing_scale",
                                       "interface_language",
                                       "model__description_language")):
    unique = {f: set() for f in fields}
    for sim in simulators.values():
        for f in fields:
            unique[f] |= set(sim.get(f, set()))
    unique = {f: sorted(unique[f]) for f in fields}
    return unique

if __name__ == "__main__":
    simulators = parse_files()
    import pprint
    pprint.pprint(simulators)

    print("unique entries per category:")
    pprint.pprint(unique_entries(simulators))