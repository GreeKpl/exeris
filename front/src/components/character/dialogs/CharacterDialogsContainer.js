import {connect} from "react-redux";
import {getDetailsType, fromDetailsState, getDetailsTarget} from "../../../modules/details";

import React from "react";
import {ReadableEntityModalContainer} from "./ReadableEntityModalContainer";
import {DIALOG_READABLE} from "../../../modules/details";

export const CharacterDialogs = ({dialogType, targetId, characterId}) => {
  switch (dialogType) {
    case DIALOG_READABLE:
      return <ReadableEntityModalContainer characterId={characterId} entityId={targetId}/>;
    default:
      return null;
  }
};


const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    dialogType: getDetailsType(fromDetailsState(state, ownProps.characterId)),
    targetId: getDetailsTarget(fromDetailsState(state, ownProps.characterId)),
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const CharacterDialogsContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CharacterDialogs);

export default CharacterDialogsContainer;
