import React from "react";
import "./style.scss";
import {Nav, NavItem, Image} from "react-bootstrap";
import actionImage from "../../../images/speakBubble.png";

/**
 * @return {XML|null}
 */
const ActionsBar = ({actions, onClick}) => {
  if (actions.length == 0) {
    return null;
  }
  return <Nav className="ActionsBar-Nav"
              style={{
                position: "fixed",
                bottom: "0px",
                left: "0px",
                right: "0px",
                height: "130px"
              }}>
    {actions.map(action =>
      <NavItem className="ActionsBar-actionItem" key={action.name}
               onClick={onClick(action.actions)}>
        <Image style={{height: "80px"}} src={actionImage} rounded/>
        <p className="ActionsBar-actionItemCaption">{action.name}</p>
      </NavItem>
    )}
  </Nav>
};

export default ActionsBar;
