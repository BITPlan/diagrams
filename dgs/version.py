"""
Created on 2023-10-05

@author: wf
"""
from dataclasses import dataclass

import dgs


@dataclass
class Version:
    """
    Version handling for nicepdf
    """

    name = "diagrams"
    version = dgs.__version__
    date = "2020-02-14"
    updated = "2023-10-28"
    description = (
        "Online diagram creation and rendering service for plantuml and graphviz"
    )

    authors = "Wolfgang Fahl"

    doc_url = "https://wiki.bitplan.com/index.php/diagrams"
    chat_url = "https://github.com/BITPlan/diagrams/discussions"
    cm_url = "https://github.com/BITPlan/diagrams"

    license = f"""Copyright 2020-2023 contributors. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied."""

    longDescription = f"""{name} version {version}
{description}

  Created by {authors} on {date} last updated {updated}"""
