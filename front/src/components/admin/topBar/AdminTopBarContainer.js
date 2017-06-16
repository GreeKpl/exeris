import React from "react";
import {Nav, NavItem} from "react-bootstrap";
import {IndexLinkContainer} from "react-router-bootstrap";
import "./style.scss";

const AdminTopBar = ({}) => {
  return <Nav bsStyle="pills"
              className="Admin-TopBar-Nav">
    <IndexLinkContainer to="/player"
                        key="main">
      <NavItem className="actionItem">
        Main
      </NavItem>
    </IndexLinkContainer>
    <IndexLinkContainer to="/admin"
                        key="admin">
      <NavItem className="actionItem">
        Admin dashboard
      </NavItem>
    </IndexLinkContainer>
    <IndexLinkContainer to="/admin/entityTypes"
                        key="entityTypes">
      <NavItem className="actionItem">
        EntityTypes
      </NavItem>
    </IndexLinkContainer>
  </Nav>;
};

export default AdminTopBar;
