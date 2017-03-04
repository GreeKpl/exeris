import DynamicName from "./DynamicName";
import {connect} from "react-redux";
import {getDynamicName, fromDynamicNamesState} from "../../modules/dynamicNames";

const mapStateToProps = (state, ownProps) => {
  return {
    observerId: ownProps.observerId,
    entityId: ownProps.entityId,
    name: getDynamicName(fromDynamicNamesState(state, ownProps.observerId)),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onClick: (actionEndpoint, entities) => event => {
      console.log("Placeholder for click on name");
    },
  }
};

const DynamicNameContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(DynamicName);

export default DynamicNameContainer;
