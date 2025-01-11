from pydantic import BaseModel
import yaml
from jinja2 import Environment, PackageLoader, select_autoescape


class Parameter(BaseModel):
    name: str
    type: str


class View(BaseModel):
    entity: str
    permissions: list[str]
    parameters: list[Parameter]
    query: str

    def get_parameters(self):
        return ", ".join([f"{p.name}: {p.type}" for p in self.parameters])

    def get_parameter_names(self):
        return ", ".join([p.name for p in self.parameters])


if __name__ == "__main__":
    with open("views.yaml") as f:
        raw_views = yaml.safe_load(f)

    views: dict[str, View] = {}
    for view_name, view_data in raw_views.items():
        views[view_name] = View(**view_data)

    entities = set([view.entity for view in views.values()])

    interfaces: dict[str, list[str]] = {}
    for entity in entities:
        interfaces[entity] = []
        for view in views.values():
            if view.entity == entity:
                for permission in view.permissions:
                    if permission.startswith(f"{entity}::"):
                        interface = permission.split("::")[1]
                        interfaces[entity].append(interface)

    value_sets = set()
    for view in views.values():
        for parameter in view.parameters:
            if parameter.type not in ["str", "int", "float", "bool"]:
                value_sets.add(parameter.type)

    env = Environment(loader=PackageLoader("main"), autoescape=select_autoescape())

    model = env.get_template("model.j2")
    model_result = model.render(
        views=views, entities=entities, interfaces=interfaces, value_sets=value_sets
    )

    client = env.get_template("client.j2")
    client_result = client.render()

    application = env.get_template("application.j2")
    application_result = application.render(
        views=views, entities=entities, value_sets=value_sets
    )

    security = env.get_template("security.j2")
    security_result = security.render()

    api = env.get_template("api.j2")
    api_result = api.render(views=views, entities=entities, value_sets=value_sets)

    with open("output/model.py", "w") as f:
        f.write(model_result)

    with open("output/client.py", "w") as f:
        f.write(client_result)

    with open("output/application.py", "w") as f:
        f.write(application_result)

    with open("output/security.py", "w") as f:
        f.write(security_result)

    with open("output/api.py", "w") as f:
        f.write(api_result)
