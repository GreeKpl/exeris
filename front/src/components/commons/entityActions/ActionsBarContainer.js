import {connect} from "react-redux";
import ActionsBar from "./ActionsBar";
import {getSelectedEntities, fromEntitiesState, getEntityInfos, getActionType} from "../../../modules/entities";
import {
  performEntityAction} from "../../../modules/entities-actionsAddon";
import * as Immutable from "immutable";

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
    && (selectedEntities.size == 1 || action.allowMultipleEntities))
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
