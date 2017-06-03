import {connect} from "react-redux";
import {getSelectedEntities, fromEntitiesState, getEntityInfos, getActionType} from "../../../modules/entities";
import {
  performEntityAction
} from "../../../modules/entities-actionsAddon";
import * as Immutable from "immutable";
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

export {ActionsBar};


export const getAllowedActions = (state, characterId) => {
  const selectedIds = getSelectedEntities(fromEntitiesState(state, characterId));
  const entities = getEntityInfos(fromEntitiesState(state, characterId));

  const selectedEntities = entities
    .filter((entityInfo, entityId) => selectedIds.has(entityId))
    .valueSeq();

  const occurrencesOfActions = selectedEntities
    .flatMap(entity => entity.get("actions"))
    .reduce((accumulator, action) => {
      const actionName = action.get("name");
      if (!accumulator[actionName]) {
        accumulator[actionName] = {count: 0, entities: []};
      }
      const actionData = accumulator[actionName];
      actionData.count += 1;
      actionData.entities.push(action.get("entity"));
      actionData.endpoint = action.get("endpoint");
      actionData.name = actionName;
      actionData.image = action.get("image");
      actionData.allowMultipleEntities = action.get("allowMultipleEntities");
      if (actionData.count > 1 && action.get("multiEntitiesName") !== null) {
        actionData.name = action.get("multiEntitiesName");
      }
      return accumulator;
    }, {});

  return Immutable.Map(occurrencesOfActions)
    .filter(action => action.count >= selectedEntities.size
    && (selectedEntities.size === 1 || action.allowMultipleEntities))
    .valueSeq().toJS();
};


const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    actions: getAllowedActions(state, ownProps.characterId),
    actionFormType: getActionType(fromEntitiesState(state, ownProps.characterId)),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onClick: (actionEndpoint, entities) => event => {
      event.preventDefault();

      dispatch(performEntityAction(ownProps.characterId, actionEndpoint, entities));
    },
  }
};

const ActionsBarContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ActionsBar);

export default ActionsBarContainer;
