local mode = Interface.GetOpArg('user.mode'):getValue()
local renderQuality = Interface.GetOpArg('user.renderQuality')
local denoise = Interface.GetOpArg('user.denoise')
local camera = Interface.GetOpArg('user.camera')
local visible = Interface.GetOpArg('user.visibilityON')
local hide = Interface.GetOpArg('user.visibilityOFF')

if mode == 0 then
    -- Initialize a GroupBuilder to store attributes
    local gb = GroupBuilder()
    gb:set('renderQuality', renderQuality)
    gb:set('denoise', denoise)
    gb:set('camera', camera)
    gb:set('visible', visible)
    gb:set('hide', hide)

    -- Set the customAttributes.renderPasses attribute
    Interface.SetAttr("customAttributes.passSettings", gb:build())
else
    -- Get previous values 
    local c_renderQuality = Interface.GetAttr('customAttributes.passSettings.renderQuality')
    local c_denoise = Interface.GetAttr('customAttributes.passSettings.denoise')
    local c_camera = Interface.GetAttr('customAttributes.passSettings.camera')
    local c_visible = Interface.GetAttr('customAttributes.passSettings.visible')
    local c_hide = Interface.GetAttr('customAttributes.passSettings.hide')


    -- Override values if they are different

    if (renderQuality ~= c_renderQuality) then
        Interface.SetAttr('customAttributes.passSettings.renderQuality', renderQuality)
    end
    if (camera ~= c_camera) and (camera ~= nil) then
        Interface.SetAttr('customAttributes.passSettings.camera', camera)
    end
    if (denoise ~= c_denoise) then
        Interface.SetAttr('customAttributes.passSettings.denoise', denoise)
    end

    if (visible ~= c_visible) and (visible ~= nil) and (visible:getValue() ~= '(())') then
        Interface.SetAttr('customAttributes.passSettings.visible', visible)
    end
    if (hide ~= c_hide) and (hide ~= nil) and (hide:getValue() ~= '(())') then
        Interface.SetAttr('customAttributes.passSettings.hide', hide)
    end
end