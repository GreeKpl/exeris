import React from "react";
import "./style.scss";
import {
  Nav,
  NavItem,
  Image,
} from "react-bootstrap";
import actionImage from "../../../images/speakBubble.png";
import {
  TakeFormContainer,
  DropFormContainer,
  GiveFormContainer,
  EatFormContainer,
  PutIntoStorageFormContainer
} from "./EntityActions";
import {
  ENTITY_ACTION_TAKE,
  ENTITY_ACTION_DROP,
  ENTITY_ACTION_GIVE,
  ENTITY_ACTION_EAT, ENTITY_ACTION_PUT_INTO_STORAGE
} from "../../../modules/entities-actionsAddon";


const FixedBar = ({children}) => <div style={{
  position: "fixed",
  bottom: "0px",
  left: "0px",
  right: "0px",
  height: "150px",
}} className="ActionsBar-bar">
  <div style={{
    height: "100%",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
  }}>
    {children}
  </div>
</div>;


/**
 * @return {XML|null}
 */
const ActionsBar = ({actionFormType, actions, onClick, characterId}) => {

  switch (actionFormType) {
    case ENTITY_ACTION_TAKE:
      return <FixedBar><TakeFormContainer characterId={characterId}/></FixedBar>;
    case ENTITY_ACTION_DROP:
      return <FixedBar><DropFormContainer characterId={characterId}/></FixedBar>;
    case ENTITY_ACTION_GIVE:
      return <FixedBar><GiveFormContainer characterId={characterId}/></FixedBar>;
    case ENTITY_ACTION_EAT:
      return <FixedBar><EatFormContainer characterId={characterId}/></FixedBar>;
    case ENTITY_ACTION_PUT_INTO_STORAGE:
      return <FixedBar><PutIntoStorageFormContainer characterId={characterId}/></FixedBar>;
    default:
      if (actions.length === 0) {
        return null;
      }

      return <Nav className="ActionsBar-bar ActionsBar-actionsList">
        {actions.map(action =>
          <NavItem className="ActionsBar-actionItem" key={action.name}
                   onClick={onClick(action.endpoint, action.entities)}>
            <Image className="ActionsBar-actionItemImage" src={actionImage} rounded/>
            <p className="ActionsBar-actionItemCaption">{action.name}</p>
          </NavItem>
        )}
      </Nav>;
  }
};

export default ActionsBar;



