import {connect} from "react-redux";
import ActionsBar from "../util/ActionsBar";
import {getSelectedEntities, fromEntitiesState, getEntityInfos, performEntityAction} from "../../../modules/entities";
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
        accumulator[actionName] = {count: 0, actions: []};
      }
      const actionData = accumulator[actionName];
      actionData.count += 1;
      actionData.actions.push({
        entity: action.get("entity"),
        endpoint: action.get("endpoint")
      });
      actionData.name = actionName;
      actionData.image = action.get("image");
      return accumulator;
    }, {});
  return Immutable.Map(occurrencesOfActions)
    .filter(action => action.count >= selectedEntities.size)
    .valueSeq().toJS();
};


const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    actions: getAllowedActions(state, ownProps.characterId),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onClick: actionsList => event => {
      event.preventDefault();
      for (let action of actionsList) {
        dispatch(performEntityAction(ownProps.characterId, action.endpoint, action.entity));
      }
    },
  }
};

const ActionsBarContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ActionsBar);

export default ActionsBarContainer;
