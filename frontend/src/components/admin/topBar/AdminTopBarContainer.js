import React from "react";
import {Nav} from "react-bootstrap";
import "./style.scss";
import {Link} from "react-router-dom";

const AdminTopBar = () => {
  return <Nav variant="pills"
              className="Admin-TopBar-Nav">
    <Nav.Item className="actionItem" key="main">
      <Nav.Link as={Link}
                to="/player">
        Main
      </Nav.Link>
    </Nav.Item>
    <Nav.Item className="actionItem" key="dashboard">
      <Nav.Link as={Link}
                to="/admin">
        Admin dashboard
      </Nav.Link>
    </Nav.Item>
    <Nav.Item className="actionItem" key="entity-types">
      <Nav.Link as={Link} to="/admin/entity-types">
        EntityTypes
      </Nav.Link>
    </Nav.Item>
  </Nav>;
};

export default AdminTopBar;
