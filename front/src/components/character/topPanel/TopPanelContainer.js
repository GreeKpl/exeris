import {connect} from "react-redux";
import {
  getDetailsType,
  fromDetailsState,
} from "../../../modules/details";
import React from "react";
import {
  PANEL_CHARACTER,
  PANEL_COMBAT,
} from "../../../modules/details";
import CombatTopPanelContainer from "./CombatTopPanelContainer";
import CharacterPanelContainer from "./CharacterPanelContainer";

/**
 * @return {XML|null}
 */
const TopPanel = ({characterId, detailsType}) => {
  switch (detailsType) {
    case PANEL_COMBAT:
      return <CombatTopPanelContainer characterId={characterId}/>;
      break;
    case PANEL_CHARACTER:
      return <CharacterPanelContainer characterId={characterId}/>;
      break;
    default:
      return null;
  }
};


export {TopPanel};


const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    detailsType: getDetailsType(fromDetailsState(state, ownProps.characterId)),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {}
};

const TopPanelContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(TopPanel);

export default TopPanelContainer;
