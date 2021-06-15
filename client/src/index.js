import _ from "lodash";
import css from "./style.css";
import BpmnModeler from "bpmn-js/lib/Modeler";
import AutoLayout from "./bpmn-auto-layout/AutoLayout";

function initForm() {
  document.getElementById("file").addEventListener("change", function (event) {
    console.log(event);
    const fileInput = event.target;
    const file = fileInput.files[0];
    if (file) {
      const extension = file.name.split(".").pop();
      if (extension == "csv") {
        const csvFields = document.getElementsByClassName("csv-fields")[0];
        csvFields.style.display = "block";
      } else {
        const csvFields = document.getElementsByClassName("csv-fields")[0];
        csvFields.style.display = "none";
      }
    }
  });
  document.addEventListener("submit", function (event) {
    event.preventDefault();
    const data = new FormData(event.target);
    console.log(...data);
    fetch("/api/upload", {
      method: "POST",
      body: data,
    })
      .then((response) => response.json())
      .then((result) => {
        console.log("Success: ", result);
        bpmnViewer.reloadView(result.xml_content);
      })
      .catch((error) => {
        console.error("Error: ", error);
      });
  });
}

var bpmnViewer = (function () {
  return {
    viewer: new BpmnModeler({
      container: "#canvas",
    }),

    layouter: new AutoLayout(),

    reloadView: async function (xml) {
      try {
        // const layoutedDiagramXML = await this.layouter.layoutProcess(xml);
        const result = await this.viewer.importXML(xml);
        // print(result);
        // console.log("rendered");
      } catch (error) {
        console.log("error rendering", error);
      }
    },
  };
})();

initForm();
