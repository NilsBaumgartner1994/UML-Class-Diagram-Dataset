# UML Class Diagram Dataset

### A Repository of Crawled UML Class Diagrams and Parsed Diagram Information

This repository is part of a large-scale scientific effort to gather, categorize, and parse UML Class Diagrams from a wide variety of sources. Our goal is to provide a comprehensive dataset for researchers and practitioners who require access to a vast array of UML Class Diagrams and their parsed information for further analysis, machine learning tasks, or to enhance understanding of software design patterns at scale.

## Dataset Overview

The dataset within this repository represents a significant portion of UML Diagrams collected from an extensive crawl from various sources. Here are the key figures highlighting the dataset's breadth:

- [script] Total Diagrams Crawled: >200,000
- [script] UML Diagrams Identified: >155,000
- [upload pending] UML Class Diagrams Found: 104,604
- [upload pending] UML Class Diagrams Parsed: 104,602

## Sources

The dataset presented in this repository has been meticulously compiled from a variety of sources, with the primary contributor being the GenMyModel platform. Below is an overview of the data provenance:

- GenMyModel Public API: A significant portion of the UML Class Diagrams was obtained via the GenMyModel Public REST API. GenMyModel is renowned for its comprehensive modeling capabilities, and the public API provides access to a rich collection of UML diagrams. The platform's commitment to sharing knowledge and resources through its API has been instrumental in allowing us to compile this extensive dataset.

The data retrieved has been processed to ensure compliance with GenMyModel's terms of service and data use policies, guaranteeing that the dataset is ethically sourced and distributed.


## Accessing the Dataset

We added in some directories a `.keep` file to keep the directory even if it is empty. The dataset is structured as follows:

```
/dataset
  /genmymodel  			 # Source
    /scripts            # Scripts for download and parsing
    /data
      /uml_diagrams          # All UML Diagrams
      /class_diagrams        # Extracted Class Diagrams
      /parsed_information    # Parsed Diagram Information
  /...    				 # Other Sources
```

To clone the repository and access the dataset, use the following command:

```
git clone https://github.com/NilsBaumgartner1994/UML-Class-Diagram-Dataset.git
```

Please note that due to the size of the dataset, special arrangements might be required to clone or download the data.


## Usage and Citation


```
@conference{umlClassDiagrams2024bBaumgartner,
  author    = {Nils Baumgartner and Elke Pulvermüller},
  title     = {An Extensive Analysis of Data Clumps in UML Class Diagrams},
  booktitle = {Proceedings of the 19th International Conference on Evaluation of Novel Approaches to Software Engineering - Volume 1: ENASE},
  year      = {2024},
  pages     = {15-26},
  publisher = {SciTePress},
  organization = {INSTICC},
  doi       = {10.5220/0012550500003687},
  isbn      = {978-989-758-696-5}
}

@misc{UMLClassDiagramDataset},
  author = {Nils Baumgartner},
  title = {UML Class Diagram Dataset},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/NilsBaumgartner1994/UML-Class-Diagram-Dataset}}
}
```

## Contributing

We welcome contributions that can help expand or enhance this dataset. If you have a collection of UML Class Diagrams or improvements to the parsing engine, please see CONTRIBUTING.md for details on submitting contributions.

<a href="https://github.com/NilsBaumgartner1994/UML-Class-Diagram-Dataset"><img src="https://contrib.rocks/image?repo=NilsBaumgartner1994/UML-Class-Diagram-Dataset" alt="Contributors" /></a>
