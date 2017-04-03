import {connect} from "react-redux";
import CharacterPanel from "./CharacterPanel";
import {
  fromTopPanelState, submitEditedName, getDetailsTarget
} from "../../../modules/topPanel";
import {parseHtmlToComponents} from "../../../util/parseDynamicName";
import {getEntityInfo, fromEntitiesState} from "../../../modules/entities";


const mapStateToProps = (state, ownProps) => {
  const targetId = getDetailsTarget(fromTopPanelState(state, ownProps.characterId));
  const entityInfo = getEntityInfo(targetId, fromEntitiesState(state, ownProps.characterId));

  const nameComponent = parseHtmlToComponents(ownProps.characterId, entityInfo.get("name"));
  return {
    characterId: ownProps.characterId,
    nameComponent: nameComponent,
    ...entityInfo.toObject(),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onSubmitName: newName => {
      dispatch(submitEditedName(ownProps.characterId, newName));
    },
  }
};

const CharacterPanelContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CharacterPanel);

export default CharacterPanelContainer;
