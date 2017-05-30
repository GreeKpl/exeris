import {connect} from "react-redux";
import {ReadableEntityModal} from "./ReadableEntityModal";
import {getEntityInfo, fromEntitiesState} from "../../../modules/entities";
import {} from "../../../modules/entities-actionsAddon";
import {closeDetails, getDetailsTarget, fromDetailsState} from "../../../modules/details";
import {performEditReadableEntityAction} from "../../../modules/entities-actionsAddon";

const mapStateToProps = (state, ownProps) => {
  const detailsTarget = getDetailsTarget(fromDetailsState(state, ownProps.characterId));
  const entityInfo = getEntityInfo(detailsTarget, fromEntitiesState(state, ownProps.characterId));
  return {
    characterId: ownProps.characterId,
    entityId: entityInfo.get("id", null),
    title: entityInfo.get("title", null),
    contents: entityInfo.get("contents", null),
    rawContents: entityInfo.get("rawContents", null),
    editable: entityInfo.get("textEditable", false),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onClose: () => {
      dispatch(closeDetails(ownProps.characterId));
    },
    onConfirmEdit: (title, contents) => {
      dispatch(performEditReadableEntityAction(ownProps.characterId, ownProps.entityId, title, contents));
    },
  };
};

export const ReadableEntityModalContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ReadableEntityModal);
