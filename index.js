require('dotenv').config();
const { Client, GatewayIntentBits, ChannelType } = require('discord.js');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMembers, // This requires SERVER MEMBERS INTENT
    GatewayIntentBits.GuildMessages
  ]
});

client.once('ready', () => {
  console.log(`✅ Logged in as ${client.user.tag}`);
  console.log(`📊 Bot is in ${client.guilds.cache.size} servers:`);
  
  // List all servers for debugging
  client.guilds.cache.forEach(guild => {
    console.log(`  🏠 ${guild.name} (${guild.id}) - ${guild.memberCount} members`);
  });
});

// Function to find appropriate welcome channel
function findWelcomeChannel(guild) {
  const welcomeChannelNames = ['welcome', 'general', 'announcements', 'lobby', 'main', 'chat'];
  
  for (const name of welcomeChannelNames) {
    const channel = guild.channels.cache.find(ch => 
      ch.type === ChannelType.GuildText && 
      ch.name.toLowerCase().includes(name) &&
      ch.permissionsFor(guild.members.me).has(['SendMessages', 'ViewChannel'])
    );
    if (channel) return channel;
  }
  
  const fallbackChannel = guild.channels.cache.find(ch => 
    ch.type === ChannelType.GuildText &&
    ch.permissionsFor(guild.members.me).has(['SendMessages', 'ViewChannel'])
  );
  
  return fallbackChannel;
}

client.on('guildMemberAdd', (member) => {
  console.log(`🔍 NEW MEMBER JOINED: ${member.user.tag} in ${member.guild.name}`);
  
  const channel = findWelcomeChannel(member.guild);
  
  if (!channel) {
    console.log(`❌ No suitable welcome channel found in ${member.guild.name}`);
    return;
  }
  
  console.log(`📍 Using channel: #${channel.name}`);
  
  channel.send(`👋 Welcome <@${member.id}> to ${member.guild.name}!`)
    .then(() => {
      console.log(`✅ Welcome message sent for ${member.user.tag}`);
    })
    .catch(error => {
      console.error(`❌ Failed to send welcome message:`, error);
    });
});

// Optional: Add test command to verify bot is working
client.on('messageCreate', (message) => {
  if (message.content === '!testbot' && !message.author.bot) {
    const channel = findWelcomeChannel(message.guild);
    message.reply(`🤖 Bot Status:\n📊 In ${client.guilds.cache.size} servers\n📍 Welcome channel: #${channel?.name || 'none found'}`);
  }
});

client.login(process.env.DISCORD_TOKEN);