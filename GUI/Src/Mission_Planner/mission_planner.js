//const LiteGraph = require("./litegraph.js/build/litegraph.js");

//Start node constructor class
function StartNode() {
    this.addOutput("Start", "string");
}

//name to show
MissionNode.title = "Start";
MissionNode.position = [10, 50];
MissionNode.size = [300, 50];

//function to call when the node is executed
MissionNode.prototype.onExecute = function() {
    this.setOutputData(0, 1);
}
//register in the system
LiteGraph.registerNodeType("basic/start", StartNode);


//Mission node constructor class
function MissionNode() {
    this.addInput("Input", "string");
    this.addOutput("Next", "string");

    this.slider_value = 0.5;
    this.number_value = 0;
    this.combo_value = "red";

    this.params = [
        {id: 0, type: "slider", value: this.slider_value},
        {id: 1, type: "number", value: this.number_value},
        {id: 2, type: "combo", value: this.combo_value}
    ];

    this.slider_widget = this.addWidget(
        "slider",
        "Slider", 
        this.slider_value, 
        function(value, widget, node){
            node.slider_value = value;
            node.params[0].value = value;
        }, 
        {min: 0, max: 1}
    );
    
    this.number_widget = this.addWidget(
        "number",
        "Number", 
        this.number_value, 
        function(value, widget, node){
            node.number_value = value;
            node.params[1].value = value;
        }, 
        { min: 0, max: 100, step: 1} 
    );

    this.combo_widget = this.addWidget(
        "combo",
        "Combo", 
        this.combo_value, 
        function(value, widget, node){
            node.combo_value = value;
            node.params[2].value = value;
        }, 
        { values:["red","green","blue"]} 
    );

    this.test_widget = this.addWidget("text","input","");
    this.toggle_widget = this.addWidget("toggle", "check");

    this.serialize_widgets = true;
}

//name to shown
MissionNode.title = "Mission";
MissionNode.position = [10, 50];
MissionNode.size = [300, 500];

//function to call when the node is executed
MissionNode.prototype.onExecute = function() {
    var A = this.getInputData(0);
    if (A === undefined)
        A = 0;
    this.setOutputData(0, A);
}
//register in the system
LiteGraph.registerNodeType("basic/mission", MissionNode);


//define the graph and canvas
var graph = new LGraph();
var canvas = new LGraphCanvas("#mycanvas", graph);

//create start node
var node_start = LiteGraph.createNode("basic/start");
node_start.pos = [25, 50];
node_start.title = "Start";
graph.add(node_start);

//create node 1
var node_mission_1 = LiteGraph.createNode("basic/mission");
node_mission_1.pos = [25, 150];
node_mission_1.title = "Mission 1";
node_mission_1.size = [200, 150];
graph.add(node_mission_1);

//create node 2
var node_mission_2 = LiteGraph.createNode("basic/mission");
node_mission_2.pos = [25, 250];  
node_mission_2.title = "Mission 2";
node_mission_2.size = [200, 150];
graph.add(node_mission_2);

//create node 3
var node_mission_3 = LiteGraph.createNode("basic/mission");
node_mission_3.pos = [25, 350];
node_mission_3.title = "Mission 3";
node_mission_3.size = [200, 150];
graph.add(node_mission_3);

//create node 4
var node_mission_4 = LiteGraph.createNode("basic/mission");
node_mission_4.pos = [25, 450];
node_mission_4.title = "Mission 4";
node_mission_4.size = [200, 150];
graph.add(node_mission_4);


canvas.allow_dragcanvas = false;
canvas.resize(650, 575);
graph.start();


let data = graph.serialize();


//define serialize button functionality
document.getElementById("convertButton").onclick = serializeData;
function serializeData() {
    let serialized_graph = graph.serialize();
    console.log(serialized_graph);

    let extracted_data = {
        links:[],
        missions:[]
    };

    let executed_nodes = [];
    let links = serialized_graph.links;
    for(let i = 0; i < links.length; i++){
        extracted_data.links[i] = [];
        extracted_data.links[i][0] = links[i][1];
        extracted_data.links[i][1] = links[i][3];

        let temp = links[i][1];
        if(!executed_nodes.includes(temp)){
            executed_nodes.push(temp);
        }
        let temp2 = links[i][3];
        if(!executed_nodes.includes(temp2)){
            executed_nodes.push(temp2);
        }
    }
    
    for(let i = 0; i < executed_nodes.length; i++){
        let node = graph.getNodeById(executed_nodes[i]);
        if(node === undefined){
            continue;
        }

        let mission = {
            id: node.id,
            type: node.title,
            params: node.params
        };

        extracted_data.missions[i] = mission;
    }

    console.log(extracted_data);
    var JSobject;
    new QWebChannel(qt.webChannelTransport, function (channel) {
        JSobject = channel.objects.Mission_Planner;
        //JSobject.sendJson(extracted_data);
        JSobject.send_json(JSON.stringify(extracted_data));
    });
    //JSobject.send_json(extracted_data);
}