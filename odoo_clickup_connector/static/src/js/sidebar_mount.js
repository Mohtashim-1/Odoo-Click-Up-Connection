// /** @odoo-module **/

// import { mount } from "@odoo/owl";
// import ClickupSidebar from "./sidebar";

// const interval = setInterval(() => {
//     const target = document.querySelector(".o_main_content");
//     if (target && !document.querySelector("#clickup-sidebar-container")) {
//         const container = document.createElement("div");
//         container.id = "clickup-sidebar-container";
//         container.className = "o_clickup_sidebar_container";
//         target.prepend(container);
//         mount(ClickupSidebar, { target: container });
//         clearInterval(interval);
//     }
// }, 500);
