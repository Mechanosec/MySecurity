# GraphQL Schema — joyreactor.cc / api.joyreactor.cc

Отримано через introspection (без авторизації).

---

## Queries

- `tagAutocomplete(mask: String!)` → `[?]!`
- `me` → `User`
- `user(username: String!)` → `User`
- `tag(name: String)` → `Tag`
- `weekTopPosts(year: Int!, week: Int!, nsfw: Boolean)` → `[?]!`
- `yearTopPosts(year: Int!, nsfw: Boolean)` → `[?]!`
- `changedPosts(day: Date!)` → `[?]!`
- `search(query: String!, tagNames: [String!], username: String, showNsfw: Boolean, showUnsafe: Boolean, showOnlyNsfw: Boolean, sortByDate: Boolean, sortByRating: Boolean, minRating: Int, maxRating: Int, searchInMyFavorites: Boolean)` → `SearchResult!`
- `initialTags(tags: [?!]!)` → `[?]!`
- `checkEmail(email: String!)` → `Boolean!`
- `searchHistory` → `SearchHistory!`
- `node(id: ID!)` → `Node`
- `donated` → `Int!`
- `trends` → `[?]!`
- `tagTopBySubscribers(nsfw: Boolean, limit: Int)` → `TagTopBySubscribers!`
- `commentTop(nsfw: Boolean)` → `CommentTop!`
- `fandomePromo` → `[?]!`

---

## Mutations

- `login(name: String!, password: String!, gid: String, did: String)` → `Query!`
- `refreshLogin(gid: String, did: String)` → `MutationResult!`
- `logout` → `Query!`
- `register(name: String!, password: String!, email: String!, did: String, captcha: String)` → `RegisterMutationResult!`
- `confirmEmail(token: String!)` → `ConfirmMutationResult!`
- `resetPassword(email: String!, token: String!, password: String!)` → `ResetMutationResult!`
- `resetPasswordRequest(email: String!)` → `MutationResult!`
- `setPhone(phone: String!)` → `MutationResult!`
- `comment(id: ID!, text: String!, files: [Upload!])` → `CommentMutationResult!`
- `post(tags: [?!]!, text: String!, files: [Upload!], poll: PollInput)` → `PostMutationResult!`
- `edit(id: ID!, text: String!, files: [Upload!])` → `Query!`
- `delete(id: ID!)` → `MutationResult!`
- `favorite(id: ID!, requestedState: Boolean!)` → `Query!`
- `favoriteTag(id: ID!, requestedState: UserTagState!)` → `Query!`
- `friend(user: ID!, requestedState: UserState!)` → `Query!`
- `vote(id: ID!, vote: VoteType!)` → `Query!`
- `pollVote(answer: ID!)` → `Query!`
- `addTagExtended(post: ID!, tag: String!)` → `MutationResult!`
- `removeTag(post: ID!, tag: ID!)` → `Query!`
- `temporaryImage(file: Upload!)` → `TemporaryImageMutationResult!`
- `ban(id: ID!, reasonCode: Int, reasonText: String, days: Int, flags: Int, tag: ID)` → `MutationResult!`
- `unban(id: ID!, reasonCode: Int, reasonText: String, flags: Int, tag: ID)` → `MutationResult!`
- `changeLocale(id: ID!, locales: [?!]!)` → `MutationResult!`
- `reportAbuse(id: ID!, reason: String!)` → `MutationResult!`
- `reportDupe(original: ID!, dupe: ID!)` → `MutationResult!`
- `proclaimDupe(original: ID!, dupe: ID!)` → `MutationResult!`
- `userSettings(settings: UserSettingsInput!, avatar: Upload)` → `MutationResult!`
- `privateMessage(user: ID!, text: String!)` → `MutationResult`
- `giftPremium(user: ID!, type: UserPremiumType!, revealGifter: Boolean)` → `MutationResult!`
- `bindBoosty(email: String!)` → `MutationResult!`
- `bindTags(ruName: String!, enName: String!)` → `MutationResult!`
- `addTagRelation(primary: ID!, secondary: ID!, type: TagRelationType!)` → `MutationResult!`
- `removeTagRelation(tag: ID!)` → `MutationResult!`
- `tagSettings(tag: ID!, settings: TagSettingsInput, image: Upload, articleImage: Upload, articlePost: ID)` → `MutationResult!`
