import React from "react";
import DashboardContainer from "../player/DashboardContainer";
import {Route, IndexRedirect} from "react-router";
import Root from "./Root";

const routes = (
  <Route path="/" component={Root}>
    <IndexRedirect to="/player"/>
    <Route path="player" component={DashboardContainer}/>
  </Route>
);

export default routes;
