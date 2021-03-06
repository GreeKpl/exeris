import {connect} from "react-redux";
import {getMyCharacterInfoFromMyCharacterState} from "../../../modules/myCharacter";
import * as Immutable from "immutable";
import React from "react";
import {Card, ProgressBar, Table} from "react-bootstrap";
import {i18nize} from "../../../i18n";


const Skill = ({name, value, indent = false}) => {
  return <tr>
    <td style={indent ? {paddingLeft: "30px"} : {}}>{name}</td>
    <td><ProgressBar now={value * 100} label={(value * 100) + "%"} striped/></td>
  </tr>;
};

class SkillsListRaw extends React.Component {
  render() {
    const {t} = this.props;

    return (
      <Card>
        <Card.Header>{t("panel_skills")}</Card.Header>
        <Card.Body>
          <Table responsive fill>
            <thead>
            <tr>
              <th>{t("skills_header_name")}</th>
              <th>{t("skills_header_level")}</th>
            </tr>
            </thead>
            <tbody>
            {this.props.mainSkills.map(generalSkill =>
              [
                <Skill
                  name={generalSkill.get("name")}
                  value={generalSkill.get("value")}
                  key={generalSkill.get("name")}
                />
              ].concat(
                generalSkill.get("children").map(specificSkill => {
                  return <Skill
                    indent={true}
                    name={specificSkill.get("name")}
                    value={specificSkill.get("value")}
                    key={specificSkill.get("name")}
                  />;
                })
              )
            )}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
    );
  }
}

export const SkillsList = i18nize(SkillsListRaw);


const mapStateToProps = (state, ownProps) => {

  const myCharacterInfo = getMyCharacterInfoFromMyCharacterState(state, ownProps.characterId);
  return {
    characterId: ownProps.characterId,
    mainSkills: myCharacterInfo.get("skills", Immutable.List()),
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const SkillsListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(SkillsList);

export default SkillsListContainer;
