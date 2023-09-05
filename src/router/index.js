import { createRouter, createWebHashHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import PayloadView from "../views/PayloadView.vue";

const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
  },
  {
    path: "/payload",
    name: "payload",
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: PayloadView,
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;
