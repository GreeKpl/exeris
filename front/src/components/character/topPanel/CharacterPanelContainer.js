import {connect} from "react-redux";
import CharacterPanel from "./CharacterPanel";
import {
  getDetailsData,
  fromTopPanelState, submitEditedName
} from "../../../modules/topPanel";
import {parseHtmlToComponents} from "../../../util/parseDynamicName";


const mapStateToProps = (state, ownProps) => {
  let allDetails = getDetailsData(fromTopPanelState(state, ownProps.characterId));
  const nameComponent = parseHtmlToComponents(ownProps.characterId, allDetails.get("name"));
  return {
    characterId: ownProps.characterId,
    nameComponent: nameComponent,
    ...allDetails.toObject(),
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
