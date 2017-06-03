import {connect} from "react-redux";
import {requestMyCharacterInfo} from "../../../modules/myCharacter";
import React from "react";
import {Grid, Row, Col, Tab, Tabs} from "react-bootstrap";
import EquipmentContainer from "./EquipmentContainer";
import InventoryListContainer from "./InventoryListContainer";
import SkillsListContainer from "./SkillsListContainer";
import AppearanceContainer from "./AppearanceContainer";
import ActionsBarContainer from "../../commons/entityActions/ActionsBarContainer";
import IntentsListContainer from "./IntentsListContainer";

export class MyCharacterPage extends React.Component {

  constructor(props) {
    super(props);
  }

  componentDidMount() {
    this.props.requestState();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.characterId !== this.props.characterId) {
      this.props.requestState();
    }
  }

  render() {

    if (this.props.isSmall) {
      return (
        <Tabs bsStyle="tabs" className="TripleNavTabsContainer" defaultActiveKey={1}>
          <Tab eventKey={1} title="Inventory">
            <InventoryListContainer characterId={this.props.characterId}/>
            <ActionsBarContainer characterId={this.props.characterId}/>
          </Tab>
          <Tab eventKey={2} title="My state">
            <IntentsListContainer characterId={this.props.characterId}/>
            <EquipmentContainer characterId={this.props.characterId}/>
          </Tab>
          <Tab eventKey={3} title="Attributes">
            <SkillsListContainer characterId={this.props.characterId}/>
            <AppearanceContainer characterId={this.props.characterId}/>
          </Tab>
        </Tabs>);
    } else {
      return (
        <div>
          <Grid fluid={true}>
            <Row>
              <Col xs={12} md={6}>
                <InventoryListContainer characterId={this.props.characterId}/>
              </Col>
              <Col xs={12} md={6}>
                <IntentsListContainer characterId={this.props.characterId}/>
                <EquipmentContainer characterId={this.props.characterId}/>
                <SkillsListContainer characterId={this.props.characterId}/>
                <AppearanceContainer characterId={this.props.characterId}/>
              </Col>
            </Row>
          </Grid>
          <ActionsBarContainer characterId={this.props.characterId}/>
        </div>);
    }
  }
}


const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.params.characterId,
    isSmall: state.get("browser").atMost.small,
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    requestState: () => dispatch(requestMyCharacterInfo(ownProps.params.characterId)),
  }
};

const MyCharacterPageContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(MyCharacterPage);

export default MyCharacterPageContainer;
