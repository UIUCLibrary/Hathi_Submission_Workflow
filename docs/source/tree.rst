Decision Tree
=============

.. graphviz::

   digraph Tree {

        start -> workflow_selection;

        workflow_selection -> "DS_selected" [dir=none,weight=1, label="Selected DS Workflow"];
        "DS_selected" -> select_package_root;
        select_package_root ->  "DS_path"[dir=none,weight=1, label="DS Workflow only"];
        "DS_path" -> select_title_pages
        select_title_pages -> process_prep;

        workflow_selection -> "brittlebooks_selected"[dir=none,weight=1, label="Selected Brittlebooks Workflow"];
        "brittlebooks_selected"-> select_package_root;
        select_package_root-> "brittlebooks_path"[dir=none,weight=1, label="Selected Brittlebooks Workflow"];
        "brittlebooks_path" ->  process_prep -> process_validate -> select_output_folder -> process_zip ->end ;

        # Middle Nodes
        "DS_selected" [shape=diamond,style=filled,label="",height=.1,width=.1]
        "DS_path" [shape=diamond,style=filled,label="",height=.1,width=.1]
        "brittlebooks_selected" [shape=diamond,style=filled,label="",height=.1,width=.1]
        "brittlebooks_path" [shape=diamond,style=filled,label="",height=.1,width=.1]

        # Nodes
        start [label="Start App"]
        workflow_selection [label="User selects workflow\nfrom options", shape=diamond]
        select_package_root [label="User selects root folder\nlocation of packages",shape=box]
        select_title_pages [label="User selects title pages\nfor each package",shape=box]
        select_output_folder [label="User selects output folder",shape=box]
        process_prep [label="User presses the \"Process\" button to\ninitiate prepping packages found in selected folder",shape=box]
        process_validate [label="User presses the \"Process\" button to\ninitiate the validation of the packages created",shape=box]
        process_zip [label="User presses the \"Process\" button to\ninitiate the zipping of packages",shape=box]
        end [label="End App"]


        # Options:
        nodesep=1.50;

        {rank=same;brittlebooks_path;DS_path}
        {rank=same;brittlebooks_selected;DS_selected}



   }
