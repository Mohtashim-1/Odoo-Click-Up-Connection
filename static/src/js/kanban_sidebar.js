// /** @odoo-module **/

// import { registry } from "@web/core/registry";

// function injectSidebarOnce() {
//     const mainContent = document.querySelector(".o_content");
//     if (!mainContent || document.querySelector("#clickup-sidebar-container")) return;

//     const sidebar = document.createElement("div");
//     sidebar.id = "clickup-sidebar-container";
//     sidebar.style = `
//         width: 200px;
//         background: #f1f1f1;
//         padding: 16px;
//         border-right: 1px solid #ccc;
//         position: absolute;
//         left: 0;
//         top: 64px;
//         bottom: 0;
//         z-index: 10;
//     `;
//     sidebar.innerHTML = `
//         <strong>ClickUp Links</strong>
//         <ul style="list-style:none; padding:0;">
//           <li><a href="#">📄 Docs</a></li>
//           <li><a href="#">📊 Dashboards</a></li>
//           <li><a href="#">🎯 Goals</a></li>
//           <li><a href="#">⏱ Timesheets</a></li>
//           <li><a href="#">📂 Spaces</a></li>
//           <li><a href="#">📁 Projects</a></li>
//         </ul>
//     `;

//     mainContent.prepend(sidebar);
// }

// registry.category("view").add("project.task.kanban", {
//     onAttach(env) {
//         setTimeout(() => injectSidebarOnce(), 1000);
//     }
// });
