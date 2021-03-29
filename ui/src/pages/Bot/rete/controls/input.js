import Rete from 'rete'
import Input from '../vue-control-components/Input'

class InputControl extends Rete.Control {
  constructor (name, emitter, label) {
    super(name)
    this.component = Input
    this.props = { name, ikey: name, emitter, label }
  }

  setValue (val) {
    this.vueContext.value = val
  }
}

export default InputControl
